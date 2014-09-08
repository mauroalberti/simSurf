# -*- coding: utf-8 -*-

"""
/***************************************************************************
 simSurf

 Simulation and deformation of georeferenced geological surfaces
                              -------------------
        version              : 0.0.1
        copyright            : (C) 2014 by Mauro Alberti - www.malg.eu
        email                : alberti.m65@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""


from __future__  import division

import os, sys

import webbrowser

from PyQt4 import QtCore
from PyQt4.QtGui import QApplication, QDialog, QGridLayout, QVBoxLayout, QWidget, QTabWidget, QToolBox, \
                        QLabel, QLineEdit, QPushButton, QRadioButton, QGroupBox, QMessageBox, QFileDialog

from math import radians, sin, cos

from numpy import *

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm


from geosurf_pure.surf_io import geosurface_export_vtk, geosurface_export_grass, geosurface_save_gas, \
                           geosurface_export_xyz, geosurface_export_esri_generate

from mpl.mpl_widget import view_3D_surface


__version__ = "0.0.1"
        
          
class GeosurfaceSimulationDialog( QDialog ):


    def __init__( self ):

        super( GeosurfaceSimulationDialog, self ).__init__() 
        self.analytical_surface_params = None
        self.geographical_surface_params = None
                            
        self.setup_gui() 


    def setup_gui( self ):

        dialog_layout = QVBoxLayout()
        main_widget = QTabWidget()
        
        main_widget.addTab( self.setup_simulation_tab(), 
                            "Simulation" ) 
                           
        main_widget.addTab( self.setup_help_tab(), 
                            "Help" ) 
                            
        dialog_layout.addWidget( main_widget )                                     
        self.setLayout( dialog_layout )                    
        self.adjustSize()                       
        self.setWindowTitle( 'simSurf - Geosurface simulation' )        
 

    def setup_simulation_tab( self ):
        
        simulWidget = QWidget()  
        simulLayout = QGridLayout( )

        simulToolBox = QToolBox()

        simulToolBox.addItem( self.setup_analformula_tb(), 
                                 "Analytical formula" )         
        simulToolBox.addItem( self.setup_geogrparams_tb(), 
                                 "Geographic parameters" )
        simulToolBox.addItem( self.setup_output_tb(), 
                                 "Output" )
                
        simulLayout.addWidget( simulToolBox, 0, 0, 1, 2 )
                                                           
        simulWidget.setLayout(simulLayout)  
                
        return simulWidget 


    def setup_analformula_tb( self ):

        analformWidget = QWidget()  
        analformLayout = QGridLayout( ) 
        
        analformLayout.addWidget( QLabel("a min"), 0, 0, 1, 1 )                
               
        self.a_min_QLineEdit = QLineEdit()
        analformLayout.addWidget( self.a_min_QLineEdit, 0, 1, 1, 1 )

        analformLayout.addWidget( QLabel("a max"), 0, 2, 1, 1 ) 
        
        self.a_max_QLineEdit = QLineEdit()
        analformLayout.addWidget( self.a_max_QLineEdit, 0, 3, 1, 1 )
        
        analformLayout.addWidget( QLabel("grid cols"), 0, 4, 1, 1 )        
        self.num_columns_QLineEdit = QLineEdit()
        analformLayout.addWidget( self.num_columns_QLineEdit, 0, 5, 1, 1 )
                                        
        analformLayout.addWidget( QLabel("b min"), 1, 0, 1, 1 )                
               
        self.b_min_QLineEdit = QLineEdit()
        analformLayout.addWidget( self.b_min_QLineEdit, 1, 1, 1, 1 )

        analformLayout.addWidget( QLabel("b max"), 1, 2, 1, 1 )
        
        self.b_max_QLineEdit = QLineEdit()
        analformLayout.addWidget( self.b_max_QLineEdit, 1, 3, 1, 1 )

        analformLayout.addWidget( QLabel("grid rows"), 1, 4, 1, 1 )        
        self.num_rows_QLineEdit = QLineEdit()
        analformLayout.addWidget( self.num_rows_QLineEdit, 1, 5, 1, 1 )
        
        analformLayout.addWidget( QLabel("Formula"), 2, 0, 1, 1 )        
        self.formula_QLineEdit = QLineEdit()
        analformLayout.addWidget( self.formula_QLineEdit, 2, 1, 1, 5 )

        analform_validate_QPushButton = QPushButton("Calculate matrix")
        analform_validate_QPushButton.clicked.connect( self.calculate_z_array )
        analformLayout.addWidget( analform_validate_QPushButton, 3, 0, 1, 6 )
        
        view_anal_surface_QPushButton = QPushButton( "View as 3D surface" )
        view_anal_surface_QPushButton.clicked[bool].connect( self.view_analytical_surface ) 
        view_anal_surface_QPushButton.setEnabled( True )       
        analformLayout.addWidget( view_anal_surface_QPushButton, 4, 0, 1, 6 )
                
        analformWidget.setLayout( analformLayout )
        
        return analformWidget
    
            
    def setup_geogrparams_tb( self ):        

        geogrparWidget = QWidget()  
        geogrparLayout = QGridLayout( ) 

        geogrparLayout.addWidget( QLabel("lower-left x"), 0, 0, 1, 1 )        
        self.geog_x_min_QLineEdit = QLineEdit()
        geogrparLayout.addWidget( self.geog_x_min_QLineEdit, 0, 1, 1, 1 )

        geogrparLayout.addWidget( QLabel("lower-left y"), 1, 0, 1, 1 )        
        self.geog_y_min_QLineEdit = QLineEdit()
        geogrparLayout.addWidget( self.geog_y_min_QLineEdit, 1, 1, 1, 1 )
        
        geogrparLayout.addWidget( QLabel("map width (x range)"), 2, 0, 1, 1 )        
        self.grid_width_QLineEdit = QLineEdit()
        geogrparLayout.addWidget( self.grid_width_QLineEdit, 2, 1, 1, 1 )        

        geogrparLayout.addWidget( QLabel("map height (y range)"), 3, 0, 1, 1 )        
        self.grid_height_QLineEdit = QLineEdit()
        geogrparLayout.addWidget( self.grid_height_QLineEdit, 3, 1, 1, 1 )
        
        geogrparLayout.addWidget( QLabel("grid rot. angle (anti-clockwise)"), 4, 0, 1, 1 )        
        self.rotation_angle_QLineEdit = QLineEdit()
        geogrparLayout.addWidget( self.rotation_angle_QLineEdit, 4, 1, 1, 1 )
                                
        simulate_surface_pButton = QPushButton( "Create simulated geosurface" )
        simulate_surface_pButton.clicked[bool].connect( self.geosurface_XYZ ) 
        simulate_surface_pButton.setEnabled( True )       
        geogrparLayout.addWidget( simulate_surface_pButton, 5, 0, 1, 2 )

        view_anal_surface_QPushButton = QPushButton( "View as 3D surface" )
        view_anal_surface_QPushButton.clicked[bool].connect( self.view_geographical_surface ) 
        view_anal_surface_QPushButton.setEnabled( True )       
        geogrparLayout.addWidget( view_anal_surface_QPushButton, 6, 0, 1, 2 )            
            
        geogrparWidget.setLayout( geogrparLayout )
        
        return geogrparWidget
 

    def setup_output_tb( self ):
 
        outputWidget = QWidget()  
        outputLayout = QGridLayout( ) 

        outputLayout.addWidget( QLabel("Format: "), 0, 0, 1, 1 )

        self.save_as_grass_QRadioButton = QRadioButton( "Grass")
        self.save_as_grass_QRadioButton.setChecked ( True )
        outputLayout.addWidget( self.save_as_grass_QRadioButton, 0, 1, 1, 1 )
                         
        self.save_as_vtk_QRadioButton = QRadioButton( "VTK")
        outputLayout.addWidget( self.save_as_vtk_QRadioButton, 0, 2, 1, 1 )

        self.save_as_gas_QRadioButton = QRadioButton( "Gas (json)")
        outputLayout.addWidget( self.save_as_gas_QRadioButton, 0, 3, 1, 1 )

        self.save_as_xyz_QRadioButton = QRadioButton( "xyz")
        outputLayout.addWidget( self.save_as_xyz_QRadioButton, 1, 1, 1, 2 ) 
  
        self.save_as_esri_generate_QRadioButton = QRadioButton( "3D ESRI generate")
        outputLayout.addWidget( self.save_as_esri_generate_QRadioButton, 1, 3, 1, 2 )
                                           
        simulation_output_browse_QPushButton = QPushButton("Save as ...")
        simulation_output_browse_QPushButton.clicked.connect( self.select_output_file )
        outputLayout.addWidget( simulation_output_browse_QPushButton, 2, 0, 1, 1 )

        self.output_filename_QLineEdit = QLineEdit()
        outputLayout.addWidget( self.output_filename_QLineEdit, 2, 1, 1, 4 )
            
        self.save_surface_pButton = QPushButton( "Save surface" )
        self.save_surface_pButton.clicked[bool].connect( self.save_surface ) 
        self.save_surface_pButton.setEnabled( True )       
        outputLayout.addWidget( self.save_surface_pButton, 3, 0, 1, 5 )        
        
        outputWidget.setLayout( outputLayout )
        
        return outputWidget       
        

    def setup_help_tab( self ):
        
        helpWidget = QWidget()  
        helpLayout = QVBoxLayout( )
        
        helpLayout.addWidget( self.setup_help() ) 

        helpWidget.setLayout(helpLayout)  
                
        return helpWidget 
  
  
    def setup_help( self ):
        
        help_QGroupBox = QGroupBox( self.tr("Help") )  
        
        helpLayout = QVBoxLayout( ) 
                
        self.help_pButton = QPushButton( "Open help in browser" )
        self.help_pButton.clicked[bool].connect( self.open_html_help ) 
        self.help_pButton.setEnabled( True )       
        helpLayout.addWidget( self.help_pButton ) 
                
        help_QGroupBox.setLayout( helpLayout )  
              
        return help_QGroupBox
                  

    def open_html_help( self ):        

        webbrowser.open('./help/help.html', new = True )
      
      
    def calculate_z_array(self):
                
        try:       
            a_min = float( eval( str( self.a_min_QLineEdit.text() ) ) ) 
            a_max = float( eval( str( self.a_max_QLineEdit.text() ) ) )      
            grid_cols = int( self.num_columns_QLineEdit.text() )                                       
                   
            b_min = float( eval( str( self.b_min_QLineEdit.text() ) ) )      
            b_max = float( eval( str( self.b_max_QLineEdit.text() ) ) )
            grid_rows = int( self.num_rows_QLineEdit.text() )            
        except:
            QMessageBox.critical( self, "Surface simulation", "Check input analytical values" )
            return            
        
        if a_min >= a_max or b_min >= b_max:
            QMessageBox.critical( self, "Surface simulation", "Check a and b values" )
            return             
            
        if grid_cols <= 0 or grid_rows <= 0:
            QMessageBox.critical( self, "Surface simulation", "Check grid column and row values" )
            return
                         
        formula = str( self.formula_QLineEdit.text() )
        if formula == '':
            QMessageBox.critical( self, "Surface simulation", "Define an analytical formula" )
            return
        
        a_array = linspace( a_min, a_max, num=grid_cols )
        b_array = linspace( b_max, b_min, num=grid_rows ) # note: reversed for conventional j order in arrays

        try:
            a_list = [ a for a in a_array for b in b_array ]
            b_list = [ b for a in a_array for b in b_array ]
            z_list = [ eval( formula ) for a in a_array for b in b_array ]
        except:
            QMessageBox.critical( self, "Surface simulation", "Error in matrix calculation" )
            return
    
        self.analytical_surface_abz = a_list, b_list, z_list 
        self.array_params = a_min, a_max, b_min, b_max 
        self.grid_dims = grid_rows, grid_cols 

        self.analytical_surface_params = {'a min': a_min,
                                          'a max': a_max,
                                          'b min': b_min,
                                          'b max': b_max,
                                          'grid cols': grid_cols,
                                          'grid rows': grid_rows,
                                          'formula': formula}
                
        QMessageBox.information( self, "Surface simulation", "Matrix created" )
        

    def view_analytical_surface( self ):

        if self.analytical_surface_params is None:
            QMessageBox.critical( self, "Surface simulation", "Matrix not yet calculated" )
            return
        view_3D_surface( self.analytical_surface_abz )
        

    def view_geographical_surface( self ):

        if self.geographical_surface_params is None:
            QMessageBox.critical( self, "Surface simulation", "Geographic surface not yet calculated" )
            return         
        view_3D_surface( self.simulated_geosurface )
        

    def calculate_scale_matrix( self, a_range, b_range, grid_height, grid_width ):
        
        assert a_range > 0.0
        assert b_range > 0.0
        assert grid_height > 0.0
        assert grid_width > 0.0
                
        sx = grid_width / a_range
        sy = grid_height / b_range
        
        return array( [ ( sx , 0.0 ) , ( 0.0, sy ) ] )
        

    def rotation_matrix( self, grid_rot_angle_degr ):
        
        grid_rot_angle_rad = radians( grid_rot_angle_degr )
        sin_rot_angle = sin( grid_rot_angle_rad )
        cos_rot_angle = cos( grid_rot_angle_rad )
        
        return array( [ ( cos_rot_angle , -sin_rot_angle ) , ( sin_rot_angle, cos_rot_angle ) ] )


    def calculate_offset_parameters( self, transformation_matrix, llc_point_matr, llc_point_geog):

        llc_point_matr_offset = dot( transformation_matrix, llc_point_matr )
                                                         
        return llc_point_geog - llc_point_matr_offset
           
                                   
    def geosurface_XYZ( self ):
        
        try:            
            geog_x_min = float( self.geog_x_min_QLineEdit.text() )        
            geog_y_min = float( self.geog_y_min_QLineEdit.text() )        

            grid_rot_angle_degr = float( self.rotation_angle_QLineEdit.text() )
            
            grid_height = float( self.grid_height_QLineEdit.text() )
            grid_width = float( self.grid_width_QLineEdit.text() )            
        except:            
            QMessageBox.critical( self, "Surface simulation", "Check input values" )
            return

        if grid_height <= 0.0 or grid_width <= 0.0:
            QMessageBox.critical( self, "Surface simulation", "Check height and width values" )
            return  
        
        try:
            X, Y, Z = self.analytical_surface_abz
            a_min, a_max, b_min, b_max = self.array_params 
            grid_rows, grid_cols = self.grid_dims  # just for checking input completeness
        except:            
            QMessageBox.critical( self, "Surface simulation", "Matrix not yet calculated" )
            return  
        
        a_range, b_range = a_max-a_min, b_max-b_min
        scale_matrix = self.calculate_scale_matrix( a_range, b_range, grid_height, grid_width )
        rotation_matrix = self.rotation_matrix( grid_rot_angle_degr )

        transformation_matrix = dot( rotation_matrix, scale_matrix )

        offset_parameters_matrix = self.calculate_offset_parameters( transformation_matrix, 
                                                                     array( [a_min, b_min] ),
                                                                     array( [geog_x_min, geog_y_min] ) )
        
        X_tr =[]; Y_tr =[]
        for x, y in zip( X, Y ):
            orig_pt = array([x,y])
            trasl_pt = dot( transformation_matrix, orig_pt) + offset_parameters_matrix
            X_tr.append( trasl_pt[0] )
            Y_tr.append( trasl_pt[1] )
            
        self.simulated_geosurface = ( X_tr, Y_tr, Z )

        self.geographical_surface_params = {'geog x min': geog_x_min,
                                            'geog y min': geog_y_min,
                                            'grid rot angle degr': grid_rot_angle_degr,
                                            'grid height': grid_height,
                                            'grid width': grid_width}
        
        QMessageBox.information( self, 
                                 "Surface simulation", 
                                 "Completed" )        
        

    def select_output_file( self ):
            
        if self.save_as_vtk_QRadioButton.isChecked():
            short_txt = "*.vtk"
            long_txt = "vtk (*.vtk *.VTK)"
        elif self.save_as_grass_QRadioButton.isChecked():
            short_txt = "*.txt"
            long_txt = "txt (*.txt *.TXT)"            
        elif self.save_as_gas_QRadioButton.isChecked():
            short_txt = "*.json"
            long_txt = "json (*.json *.JSON)" 
        elif self.save_as_xyz_QRadioButton.isChecked():
            short_txt = "*.xyz"
            long_txt = "xyz (*.xyz *.XYZ)" 
        elif self.save_as_esri_generate_QRadioButton.isChecked():
            short_txt = "*.*"
            long_txt = "generate file (*.*)"             
                                                         
        output_filename = QFileDialog.getSaveFileName(self, 
                                                      self.tr( "Save as" ), 
                                                      short_txt, 
                                                      long_txt )        
        if not output_filename:
            return

        self.output_filename_QLineEdit.setText( output_filename ) 
        

    def save_surface( self ):
        
        try:
            self.simulated_geosurface
        except AttributeError:
            QMessageBox.critical( self, "Surface saving", "Geosurface is not yet defined" )
            return            

        geodata = self.simulated_geosurface, self.grid_dims        
        if self.save_as_vtk_QRadioButton.isChecked():
            save_function = geosurface_export_vtk
        elif self.save_as_grass_QRadioButton.isChecked():
            save_function = geosurface_export_grass 
        elif self.save_as_xyz_QRadioButton.isChecked():
            save_function = geosurface_export_xyz            
        elif self.save_as_gas_QRadioButton.isChecked():
            save_function = geosurface_save_gas
            geodata = {'analytical surface': self.analytical_surface_params,
                       'geographical params': self.geographical_surface_params }        
        elif self.save_as_esri_generate_QRadioButton.isChecked():
            save_function = geosurface_export_esri_generate
            
        done = save_function( self.output_filename_QLineEdit.text(), geodata )
        
        if done:
            QMessageBox.information( self, "Surface saving", "Done" )
        else:
            QMessageBox.critical( self, "Surface saving", "Some errors occurred" )

                
def main():
    """
    Main of the module.
    """    
    app = QApplication(sys.argv)    
    form = GeosurfaceSimulationDialog()
    form.show()
    app.exec_()


main()








         
