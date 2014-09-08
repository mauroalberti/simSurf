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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
 
from geosurf_pure.spatial import AnalyticGeosurface
from geosurf_pure.surf_io import geosurface_export_vtk, geosurface_export_grass, geosurface_save_gas, \
                           geosurface_read_gas_input, geosurface_export_esri_generate, geosurface_export_xyz
from geosurf_pure.errors import AnaliticSurfaceIOException, AnaliticSurfaceCalcException
 
from mpl.mpl_widget import view_3D_surface
 
 
__version__ = "0.0.1"

      
        
class GeosurfaceDeformationDialog( QDialog ):
    

    def __init__( self ):

        super( GeosurfaceDeformationDialog, self ).__init__() 
                            
        self.setup_gui() 


    def setup_gui( self ):

        dialog_layout = QVBoxLayout()
        main_widget = QTabWidget()
        
        main_widget.addTab( self.setup_main_tab(), 
                            "3D surface deformation" ) 
                           
        main_widget.addTab( self.setup_help_tab(), 
                            "Help" ) 
                            
        dialog_layout.addWidget( main_widget )                                     
        self.setLayout( dialog_layout )                    
        self.adjustSize()                       
        self.setWindowTitle( 'simSurf - Geosurface deformation' )        
 

    def setup_main_tab( self ):
        
        simulWidget = QWidget()  
        simulLayout = QGridLayout( )

        simulToolBox = QToolBox()

        simulToolBox.addItem( self.setup_input_tb(), 
                                 "Input geosurface" )         
        simulToolBox.addItem( self.setup_deformation_tb(), 
                                 "Apply deformation" )
        simulToolBox.addItem( self.setup_output_tb(), 
                                 "Output" )
                
        simulLayout.addWidget( simulToolBox, 0, 0, 1, 2 )
                                                           
        simulWidget.setLayout(simulLayout)  
                
        return simulWidget 


    def setup_input_tb( self ):

        inputformWidget = QWidget()  
        inputformLayout = QGridLayout( ) 
      
        input_browse_QPushButton = QPushButton("Source file ...")
        input_browse_QPushButton.clicked.connect( self.select_input_file )
        inputformLayout.addWidget( input_browse_QPushButton, 0, 0, 1, 1 )
        
        self.input_filename_QLineEdit = QLineEdit()
        inputformLayout.addWidget( self.input_filename_QLineEdit, 0, 1, 1, 2 )
        
        load_geosurface_QPushButton = QPushButton( "Load geosurface" )
        load_geosurface_QPushButton.clicked[bool].connect( self.load_input_geosurface ) 
        load_geosurface_QPushButton.setEnabled( True )       
        inputformLayout.addWidget( load_geosurface_QPushButton, 2, 0, 1, 3 )
                
        inputformWidget.setLayout( inputformLayout )
        
        return inputformWidget
    
            
    def setup_deformation_tb( self ):        

        deformationWidget = QWidget()  
        deformationLayout = QGridLayout( ) 

        displacement_QPushButton = QPushButton( "Displacement" )
        displacement_QPushButton.clicked[bool].connect( self.do_displacement ) 
        displacement_QPushButton.setEnabled( True )       
        deformationLayout.addWidget( displacement_QPushButton, 0, 0, 1, 1 )

        rotation_QPushButton = QPushButton( "Rotation" )
        rotation_QPushButton.clicked[bool].connect( self.do_rotation ) 
        rotation_QPushButton.setEnabled( True )       
        deformationLayout.addWidget( rotation_QPushButton, 1, 0, 1, 1 )
                    
        scaling_QPushButton = QPushButton( "Scaling" )
        scaling_QPushButton.clicked[bool].connect( self.do_scaling ) 
        scaling_QPushButton.setEnabled( True )       
        deformationLayout.addWidget( scaling_QPushButton, 2, 0, 1, 1 )                    
                    
        hor_shear_QPushButton = QPushButton( "Horizontal simple shear" )
        hor_shear_QPushButton.clicked[bool].connect( self.do_horiz_shear ) 
        hor_shear_QPushButton.setEnabled( True )       
        deformationLayout.addWidget( hor_shear_QPushButton, 3, 0, 1, 1 )

        vert_shear_QPushButton = QPushButton( "Vertical simple shear" )
        vert_shear_QPushButton.clicked[bool].connect( self.do_vert_shear ) 
        vert_shear_QPushButton.setEnabled( True )       
        deformationLayout.addWidget( vert_shear_QPushButton, 4, 0, 1, 1 )
                                                            
        deformationWidget.setLayout( deformationLayout )
        
        return deformationWidget

        
    def setup_visualization_tb( self ):
        
        visualWidget = QWidget()  
        visualLayout = QGridLayout() 
        
        self.view_geosurface_QPushButton = QPushButton( "Plot surface" )
        self.view_geosurface_QPushButton.clicked[bool].connect( self.view_geosurface ) 
        self.view_geosurface_QPushButton.setEnabled( True )       
        visualLayout.addWidget( self.view_geosurface_QPushButton, 0, 0, 1, 1 )         
            
        
        visualWidget.setLayout( visualLayout )
        
        return visualWidget
    
    
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

        self.simulation_outputfilename_QLineEdit = QLineEdit()
        outputLayout.addWidget( self.simulation_outputfilename_QLineEdit, 2, 1, 1, 4 )
            
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
      

    def select_input_file( self ):
            
        short_txt = "*.json"
        long_txt = "json (*.json *.JSON)"            
                                 
        input_filename = QFileDialog.getOpenFileName(self, 
                                                      self.tr( "Open file: " ), 
                                                      short_txt, 
                                                      long_txt )        
        if not input_filename:
            return

        self.input_filename_QLineEdit.setText( input_filename ) 
 
    
    def create_geosurface( self ):
        
        self.anal_geosurface = AnalyticGeosurface( self.analytical_params, self.geographical_params, self.deformational_params ) 
        self.geosurface_xyz_values =  self.anal_geosurface.geosurface_XYZ()
            

    def load_input_geosurface(self):

        try:
            self.analytical_params, self.geographical_params, self.deformational_params = geosurface_read_gas_input( self.input_filename_QLineEdit.text() )
            self.create_geosurface()                  
        except ( AnaliticSurfaceIOException, AnaliticSurfaceCalcException ), msg:
            QMessageBox.critical( self, "Surface import", str(msg) )
            return  
        
        QMessageBox.information( self, "Surface load", "Done" ) 
   

    def test_input_geosurface( self, header ):

        try:
            self.geosurface_xyz_values
            return True
        except:
            QMessageBox.critical( self, header,"No loaded geosurface" )
            return False
            
        
    def do_displacement( self ):
        
        if not self.test_input_geosurface("Displacement"):  return
        
        self.displacement_window = GeosurfaceDisplacementDialog( )       
        QObject.connect( self.displacement_window, SIGNAL( "update_geosurface_for_displacement" ), self.update_displacement )
        self.displacement_window.show()
                          

    def do_rotation( self ):

        if not self.test_input_geosurface("Rotation"):  return        
            
        self.rotation_window = GeosurfaceRotationDialog( self.anal_geosurface.geosurface_center() )       
        QObject.connect( self.rotation_window, SIGNAL( "update_geosurface_for_rotation" ), self.update_rotation )
        self.rotation_window.show()
        

    def do_scaling( self ):
        
        if not self.test_input_geosurface("Scaling"):  return        
           
        self.scaling_window = GeosurfaceScalingDialog( self.anal_geosurface.geosurface_center() )       
        QObject.connect( self.scaling_window, SIGNAL( "update_geosurface_for_scaling" ), self.update_scaling )
        self.scaling_window.show()        


    def do_horiz_shear( self ):
        
        if not self.test_input_geosurface("Simple shear (horizontal)"):  return        
         
        self.horiz_shear_window = GeosurfaceHorizShearDialog( self.anal_geosurface.geosurface_center() )       
        QObject.connect( self.horiz_shear_window, SIGNAL( "update_geosurface_for_horiz_shear" ), self.update_horiz_shear )
        self.horiz_shear_window.show()
        

    def do_vert_shear( self ):
        
        if not self.test_input_geosurface("Simple shear (vertical)"):  return        
         
        self.vert_shear_window = GeosurfaceVertShearDialog( self.anal_geosurface.geosurface_center() )       
        QObject.connect( self.vert_shear_window, SIGNAL( "update_geosurface_for_vert_shear" ), self.update_vert_shear )
        self.vert_shear_window.show()


    def update_displacement( self ):

        # get displacement values
        try:
            delta_x = float( self.displacement_window.delta_x_QLineEdit.text() )
            delta_y = float( self.displacement_window.delta_y_QLineEdit.text() )
            delta_z = float( self.displacement_window.delta_z_QLineEdit.text() )
        except:
            QMessageBox.critical( self, "Displacement", "Error in input values" )
            return             
                
        self.deformational_params.append( {'type':'displacement', 
                                           'parameters': {'delta_x' : delta_x, 
                                                          'delta_y' : delta_y, 
                                                          'delta_z' : delta_z } } )

        try:
            self.create_geosurface()
        except AnaliticSurfaceCalcException, msg:
            QMessageBox.critical( self, "Surface displacement", str(msg) )
        else:
            QMessageBox.information( self, "Surface displacement", "Done" ) 


    def update_rotation( self ):
        
        # get rotation values
        try:
            rot_axis_trend = float( self.rotation_window.axis_trend_QDSpinBox.value() )
            rot_axis_plunge = float( self.rotation_window.axis_plunge_QDSpinBox.value() )
            rot_angle_degr = float( self.rotation_window.rotation_angle_QDSpinBox.value() )
            
            center_x = float( self.rotation_window.axis_center_x_QDSpinBox.value() )
            center_y = float( self.rotation_window.axis_center_y_QDSpinBox.value() )            
            center_z = float( self.rotation_window.axis_center_z_QDSpinBox.value() )            
        except:
            QMessageBox.critical( self, "Rotation", "Error in input values" )
            return          
        
        self.deformational_params.append( {'type':'rotation', 
                                       'parameters': {'rotation axis trend' : rot_axis_trend, 
                                                      'rotation axis plunge' : rot_axis_plunge, 
                                                      'rotation angle' : rot_angle_degr,
                                                      'center x': center_x,
                                                      'center y': center_y,
                                                      'center z': center_z, } } )

        try:
            self.create_geosurface()
        except AnaliticSurfaceCalcException, msg:
            QMessageBox.critical( self, "Surface rotation", str(msg) )
        else:
            QMessageBox.information( self, "Surface rotation", "Done" ) 
        
 
    def update_scaling( self ):
        
        # get scaling parameters
        try:
            scale_factor_x = float( self.scaling_window.scale_x_QLineEdit.text() )
            scale_factor_y = float( self.scaling_window.scale_y_QLineEdit.text() )
            scale_factor_z = float( self.scaling_window.scale_z_QLineEdit.text() )
            
            center_x = float( self.scaling_window.axis_center_x_QDSpinBox.value() )
            center_y = float( self.scaling_window.axis_center_y_QDSpinBox.value() )            
            center_z = float( self.scaling_window.axis_center_z_QDSpinBox.value() )    
        except:
            QMessageBox.critical( self, "Scaling", "Error in input values" )
            return          
        
        if scale_factor_x == 0.0 or scale_factor_y == 0.0 or scale_factor_z == 0.0:
            QMessageBox.critical( self, "Scaling", "Input value(s) cannot be zero" )
            return
                
        self.deformational_params.append( {'type':'scaling', 
                                           'parameters': {'x factor' : scale_factor_x, 
                                                          'y factor' : scale_factor_y, 
                                                          'z factor' : scale_factor_z,
                                                          'center x': center_x,
                                                          'center y': center_y,
                                                          'center z': center_z, } } )

        try:
            self.create_geosurface()
        except AnaliticSurfaceCalcException, msg:
            QMessageBox.critical( self, "Surface scaling", str(msg) )
        else:
            QMessageBox.information( self, "Surface scaling", "Done" ) 
            

    def update_horiz_shear( self ):
        
        # get horizontal shear values
        try:
            psi_angle_degr = float( self.horiz_shear_window.psi_QDSpinBox.value() )
            alpha_angle_degr = float( self.horiz_shear_window.alpha_QDSpinBox.value() )
            
            center_x = float( self.horiz_shear_window.axis_center_x_QDSpinBox.value() )
            center_y = float( self.horiz_shear_window.axis_center_y_QDSpinBox.value() )            
            center_z = float( self.horiz_shear_window.axis_center_z_QDSpinBox.value() )    
        except:
            QMessageBox.critical( self, "Simple shear (horizontal)", "Error in input values" )
            return          
        
        self.deformational_params.append( {'type':'simple shear - horizontal', 
                                           'parameters': {'psi angle (degr.)' : psi_angle_degr, 
                                                          'alpha angle (degr.)' : alpha_angle_degr,
                                                          'center x': center_x,
                                                          'center y': center_y,
                                                          'center z': center_z, } } )

        try:
            self.create_geosurface()
        except AnaliticSurfaceCalcException, msg:
            QMessageBox.critical( self, "Surface simple shear (horiz.)", str(msg) )
        else:
            QMessageBox.information( self, "Surface simple shear (horiz.)", "Done" ) 
 
 
    def update_vert_shear( self ):
        
        # get vertical shear values
        try:
            psi_angle_degr = float( self.vert_shear_window.psi_QDSpinBox.value() )
            alpha_angle_degr = float( self.vert_shear_window.alpha_QDSpinBox.value() )
            
            center_x = float( self.vert_shear_window.axis_center_x_QDSpinBox.value() )
            center_y = float( self.vert_shear_window.axis_center_y_QDSpinBox.value() )            
            center_z = float( self.vert_shear_window.axis_center_z_QDSpinBox.value() )                
        except:
            QMessageBox.critical( self, "Simple shear (vertical)", "Error in input values" )
            return          
        
        self.deformational_params.append( {'type':'simple shear - vertical', 
                                           'parameters': {'psi angle (degr.)' : psi_angle_degr, 
                                                          'alpha angle (degr.)' : alpha_angle_degr,
                                                          'center x': center_x,
                                                          'center y': center_y,
                                                          'center z': center_z, } } )
        try:
            self.create_geosurface()
        except AnaliticSurfaceCalcException, msg:
            QMessageBox.critical( self, "Surface simple shear (vert.)", str(msg) )
        else:
            QMessageBox.information( self, "Surface simple shear (vert.)", "Done" ) 

    
    def view_geosurface( self ):
 
        try:        
            geosurface_xyz_values = self.geosurface_xyz_values
        except:
            QMessageBox.critical( self, "Surface deformation", "Analytical surface not defined" )

        if geosurface_xyz_values:
            try:          
                view_3D_surface( geosurface_xyz_values )
            except:
                QMessageBox.critical( self, "Surface view", "Unable to create plot. Try exporting as VTK/Grass and using Paraview or Grass for visualization" )                
        else:
            QMessageBox.critical( self, "Surface deformation", "Geological surface not defined" )
        
                
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
        if output_filename:
            self.simulation_outputfilename_QLineEdit.setText( output_filename )  


    def save_surface( self ):
        
        try:
            self.geosurface_xyz_values
        except AttributeError:
            QMessageBox.critical( self, "Surface saving", "Geosurface is not yet defined" )
            return            
  
        geodata = self.geosurface_xyz_values, self.anal_geosurface.anal_param_values[1]
        if self.save_as_vtk_QRadioButton.isChecked():
            save_function = geosurface_export_vtk
        elif self.save_as_grass_QRadioButton.isChecked():
            save_function = geosurface_export_grass 
        elif self.save_as_xyz_QRadioButton.isChecked():
            save_function = geosurface_export_xyz                 
        elif self.save_as_gas_QRadioButton.isChecked():
            save_function = geosurface_save_gas
            geodata = {'analytical surface': self.analytical_params,
                       'geographical params': self.geographical_params,
                       'deformational params': self.anal_geosurface.deformational_params }
        elif self.save_as_esri_generate_QRadioButton.isChecked():
            save_function = geosurface_export_esri_generate
                 
        done = save_function( self.simulation_outputfilename_QLineEdit.text(), geodata )
        
        if done:
            QMessageBox.information( self, "Surface saving", "Done" )
        else:
            QMessageBox.critical( self, "Surface saving", "Some errors occurred" )         
            
            

class GeosurfaceDisplacementDialog( QDialog ):

    def __init__( self ):

        super( GeosurfaceDisplacementDialog, self ).__init__() 
  
        displLayout = QGridLayout( )                            
                        
        displLayout.addWidget( QLabel("X offset"), 0, 0, 1, 1 )             
        self.delta_x_QLineEdit = QLineEdit()
        displLayout.addWidget( self.delta_x_QLineEdit, 0, 1, 1, 1 )

        displLayout.addWidget( QLabel("Y offset"), 1, 0, 1, 1 )             
        self.delta_y_QLineEdit = QLineEdit()
        displLayout.addWidget( self.delta_y_QLineEdit, 1, 1, 1, 1 )
        
        displLayout.addWidget( QLabel("Z offset"), 2, 0, 1, 1 )             
        self.delta_z_QLineEdit = QLineEdit()
        displLayout.addWidget( self.delta_z_QLineEdit, 2, 1, 1, 1 )          

        done_QPushButton = QPushButton( "Apply" )
        done_QPushButton.clicked[bool].connect( self.displacement_done ) 
        done_QPushButton.setEnabled( True ) 
              
        displLayout.addWidget( done_QPushButton, 3, 0, 1, 2 )
                                                                         
        self.setLayout( displLayout )         
        self.adjustSize()                       
        self.setWindowTitle( 'Displacement' ) 
         
        
    def displacement_done( self, dummy_var ):        

        self.emit( SIGNAL( "update_geosurface_for_displacement" ) )                       
        self.close()
        
 

class GeosurfaceRotationDialog( QDialog ):

    def __init__( self, geosurface_center ):

        super( GeosurfaceRotationDialog, self ).__init__() 
  
        self.geosurface_center = geosurface_center
        
        displLayout = QGridLayout()  
                                       
        displLayout.addWidget( QLabel("Rotation axis and angle"), 0, 0, 1, 3 )             
        
        displLayout.addWidget( QLabel("trend"), 1, 0, 1, 1 )  
                   
        self.axis_trend_QDSpinBox = QDoubleSpinBox()
        self.axis_trend_QDSpinBox.setMaximum( 360.0 )
        self.axis_trend_QDSpinBox.setSingleStep( 0.1 )        
        displLayout.addWidget( self.axis_trend_QDSpinBox, 1, 1, 1, 1 )

        displLayout.addWidget( QLabel("plunge"), 1, 2, 1, 1 )   
                  
        self.axis_plunge_QDSpinBox = QDoubleSpinBox()
        self.axis_plunge_QDSpinBox.setMinimum( -90.0 )
        self.axis_plunge_QDSpinBox.setMaximum( 90.0 )
        self.axis_plunge_QDSpinBox.setSingleStep( 0.1 )        
        displLayout.addWidget( self.axis_plunge_QDSpinBox, 1, 3, 1, 1 )                

        displLayout.addWidget( QLabel("angle"), 1, 4, 1, 1 )  
                  
        self.rotation_angle_QDSpinBox = QDoubleSpinBox()
        self.rotation_angle_QDSpinBox.setMinimum( -360.0 )
        self.rotation_angle_QDSpinBox.setMaximum( 360.0 )
        self.rotation_angle_QDSpinBox.setSingleStep( 0.1 )        
        displLayout.addWidget( self.rotation_angle_QDSpinBox, 1, 5, 1, 1 )          

                  
        displLayout.addWidget( QLabel("Rotation center"), 2, 0, 1, 2 )                  
 
        displLayout.addWidget( QLabel("x"), 3, 0, 1, 1 ) 


        range_extreme = 9999999999 
        self.axis_center_x_QDSpinBox = QDoubleSpinBox()
        self.axis_center_x_QDSpinBox.setRange( -range_extreme, range_extreme )
        self.axis_center_x_QDSpinBox.setSingleStep( 0.1 )        
        displLayout.addWidget( self.axis_center_x_QDSpinBox, 3, 1, 1, 1 )         

        displLayout.addWidget( QLabel("y"), 3, 2, 1, 1 ) 

        self.axis_center_y_QDSpinBox = QDoubleSpinBox()
        self.axis_center_y_QDSpinBox.setRange( -range_extreme, range_extreme )
        self.axis_center_y_QDSpinBox.setSingleStep( 0.1 )        
        displLayout.addWidget( self.axis_center_y_QDSpinBox, 3, 3, 1, 1 )   
        
        displLayout.addWidget( QLabel("z"), 3, 4, 1, 1 ) 

        self.axis_center_z_QDSpinBox = QDoubleSpinBox()
        self.axis_center_z_QDSpinBox.setRange( -range_extreme, range_extreme )
        self.axis_center_z_QDSpinBox.setSingleStep( 0.1 )        
        displLayout.addWidget( self.axis_center_z_QDSpinBox, 3, 5, 1, 1 )   
                                      
        self.axis_center_choice_QCheckBox = QCheckBox("fix rotation center to geosurface center")
        self.axis_center_choice_QCheckBox.setChecked( True ) 
        self.axis_center_choice_QCheckBox.stateChanged.connect( self.set_center_values )
        displLayout.addWidget( self.axis_center_choice_QCheckBox, 4, 0, 1, 4 )                             

        self.set_center_values( )
            
            
        done_QPushButton = QPushButton( "Apply" )
        done_QPushButton.clicked[bool].connect( self.rotation_done ) 
        done_QPushButton.setEnabled( True )               
        displLayout.addWidget( done_QPushButton, 5, 0, 1, 6 )
                                                                         
        self.setLayout( displLayout )         
        self.adjustSize()                       
        self.setWindowTitle( 'Rotation' ) 
         

    def set_center_values( self ):

        if self.axis_center_choice_QCheckBox.isChecked():        
            self.axis_center_x_QDSpinBox.setValue( self.geosurface_center[0] ) 
            self.axis_center_y_QDSpinBox.setValue( self.geosurface_center[1] )        
            self.axis_center_z_QDSpinBox.setValue( self.geosurface_center[2] )
                
                
    def rotation_done( self, dummy_var ):        

        self.emit( SIGNAL( "update_geosurface_for_rotation" ) )                       
        self.close()
   
   

class GeosurfaceScalingDialog( QDialog ):

    def __init__( self, geosurface_center ):

        super( GeosurfaceScalingDialog, self ).__init__() 
 
        self.geosurface_center = geosurface_center
         
        scalingLayout = QGridLayout( )                            

        scalingLayout.addWidget( QLabel("Scale factors"), 0, 0, 1, 2 )
                                
        scalingLayout.addWidget( QLabel("x"), 1, 0, 1, 1 )             
        self.scale_x_QLineEdit = QLineEdit()
        scalingLayout.addWidget( self.scale_x_QLineEdit, 1, 1, 1, 1 )

        scalingLayout.addWidget( QLabel("y"), 1, 2, 1, 1 )             
        self.scale_y_QLineEdit = QLineEdit()
        scalingLayout.addWidget( self.scale_y_QLineEdit, 1, 3, 1, 1 )
        
        scalingLayout.addWidget( QLabel("z"), 1, 4, 1, 1 )             
        self.scale_z_QLineEdit = QLineEdit()
        scalingLayout.addWidget( self.scale_z_QLineEdit, 1, 5, 1, 1 )          

                  
        scalingLayout.addWidget( QLabel("Scaling center"), 2, 0, 1, 2 )                  
 
        scalingLayout.addWidget( QLabel("x"), 3, 0, 1, 1 ) 


        range_extreme = 9999999999 
        self.axis_center_x_QDSpinBox = QDoubleSpinBox()
        self.axis_center_x_QDSpinBox.setRange( -range_extreme, range_extreme )
        self.axis_center_x_QDSpinBox.setSingleStep( 0.1 )        
        scalingLayout.addWidget( self.axis_center_x_QDSpinBox, 3, 1, 1, 1 )         

        scalingLayout.addWidget( QLabel("y"), 3, 2, 1, 1 ) 

        self.axis_center_y_QDSpinBox = QDoubleSpinBox()
        self.axis_center_y_QDSpinBox.setRange( -range_extreme, range_extreme )
        self.axis_center_y_QDSpinBox.setSingleStep( 0.1 )        
        scalingLayout.addWidget( self.axis_center_y_QDSpinBox, 3, 3, 1, 1 )   
        
        scalingLayout.addWidget( QLabel("z"), 3, 4, 1, 1 ) 

        self.axis_center_z_QDSpinBox = QDoubleSpinBox()
        self.axis_center_z_QDSpinBox.setRange( -range_extreme, range_extreme )
        self.axis_center_z_QDSpinBox.setSingleStep( 0.1 )        
        scalingLayout.addWidget( self.axis_center_z_QDSpinBox, 3, 5, 1, 1 )   
                                      
        self.axis_center_choice_QCheckBox = QCheckBox("fix scaling center to geosurface center")
        self.axis_center_choice_QCheckBox.setChecked( True ) 
        self.axis_center_choice_QCheckBox.stateChanged.connect( self.set_center_values )
        scalingLayout.addWidget( self.axis_center_choice_QCheckBox, 4, 0, 1, 4 )                             

        self.set_center_values( )


        done_QPushButton = QPushButton( "Apply" )
        done_QPushButton.clicked[bool].connect( self.scaling_done ) 
        done_QPushButton.setEnabled( True ) 
              
        scalingLayout.addWidget( done_QPushButton, 5, 0, 1, 6 )
                                                                         
        self.setLayout( scalingLayout )         
        self.adjustSize()                       
        self.setWindowTitle( 'Scaling' ) 
         

    def set_center_values( self ):

        if self.axis_center_choice_QCheckBox.isChecked():        
            self.axis_center_x_QDSpinBox.setValue( self.geosurface_center[0] ) 
            self.axis_center_y_QDSpinBox.setValue( self.geosurface_center[1] )        
            self.axis_center_z_QDSpinBox.setValue( self.geosurface_center[2] )
            
             
    def scaling_done( self, dummy_var ):        

        self.emit( SIGNAL( "update_geosurface_for_scaling" ) )                       
        self.close()
 
 
class GeosurfaceHorizShearDialog( QDialog ):
     
    def __init__( self, geosurface_center ):

        super( GeosurfaceHorizShearDialog, self ).__init__() 
 
        self.geosurface_center = geosurface_center
         
        simpleshear_horizLayout = QGridLayout( )                            
                    
        simpleshear_horizLayout.addWidget( QLabel("Psi"), 0, 0, 1, 1 )  

        self.psi_QDSpinBox = QDoubleSpinBox()
        self.psi_QDSpinBox.setRange( 0.0, 89.9 )
        self.psi_QDSpinBox.setSingleStep( 0.1 )        
        simpleshear_horizLayout.addWidget( self.psi_QDSpinBox, 0, 1, 1, 1 )

        simpleshear_horizLayout.addWidget( QLabel("Alpha"), 0, 2, 1, 1 )  
        
        self.alpha_QDSpinBox = QDoubleSpinBox()
        self.alpha_QDSpinBox.setRange( 0.0, 359.9 )
        self.alpha_QDSpinBox.setSingleStep( 0.1 )             
        simpleshear_horizLayout.addWidget( self.alpha_QDSpinBox, 0, 3, 1, 1 )
               
                  
        simpleshear_horizLayout.addWidget( QLabel("Shear axis center"), 1, 0, 1, 2 )                  
 
        simpleshear_horizLayout.addWidget( QLabel("x"), 2, 0, 1, 1 ) 


        range_extreme = 9999999999 
        self.axis_center_x_QDSpinBox = QDoubleSpinBox()
        self.axis_center_x_QDSpinBox.setRange( -range_extreme, range_extreme )
        self.axis_center_x_QDSpinBox.setSingleStep( 0.1 )        
        simpleshear_horizLayout.addWidget( self.axis_center_x_QDSpinBox, 2, 1, 1, 1 )         

        simpleshear_horizLayout.addWidget( QLabel("y"), 2, 2, 1, 1 ) 

        self.axis_center_y_QDSpinBox = QDoubleSpinBox()
        self.axis_center_y_QDSpinBox.setRange( -range_extreme, range_extreme )
        self.axis_center_y_QDSpinBox.setSingleStep( 0.1 )        
        simpleshear_horizLayout.addWidget( self.axis_center_y_QDSpinBox, 2, 3, 1, 1 )   
        
        simpleshear_horizLayout.addWidget( QLabel("z"), 2, 4, 1, 1 ) 

        self.axis_center_z_QDSpinBox = QDoubleSpinBox()
        self.axis_center_z_QDSpinBox.setRange( -range_extreme, range_extreme )
        self.axis_center_z_QDSpinBox.setSingleStep( 0.1 )        
        simpleshear_horizLayout.addWidget( self.axis_center_z_QDSpinBox, 2, 5, 1, 1 )   
                                      
        self.axis_center_choice_QCheckBox = QCheckBox("fix shear axis center to geosurface center")
        self.axis_center_choice_QCheckBox.setChecked( True ) 
        self.axis_center_choice_QCheckBox.stateChanged.connect( self.set_center_values )
        simpleshear_horizLayout.addWidget( self.axis_center_choice_QCheckBox, 3, 0, 1, 4 )                             

        self.set_center_values( )

        done_QPushButton = QPushButton( "Apply" )
        done_QPushButton.clicked[bool].connect( self.horiz_shear_done ) 
        done_QPushButton.setEnabled( True ) 
              
        simpleshear_horizLayout.addWidget( done_QPushButton, 4, 0, 1, 6 )
                                                                         
        self.setLayout( simpleshear_horizLayout )         
        self.adjustSize()                       
        self.setWindowTitle( 'Horizontal simple shear' ) 
         
 
    def set_center_values( self ):

        if self.axis_center_choice_QCheckBox.isChecked():        
            self.axis_center_x_QDSpinBox.setValue( self.geosurface_center[0] ) 
            self.axis_center_y_QDSpinBox.setValue( self.geosurface_center[1] )        
            self.axis_center_z_QDSpinBox.setValue( self.geosurface_center[2] )
            
            
    def horiz_shear_done( self, dummy_var ):        

        self.emit( SIGNAL( "update_geosurface_for_horiz_shear" ) )                       
        self.close()
        
             
class GeosurfaceVertShearDialog( QDialog ):
     
    def __init__( self, geosurface_center ):

        super( GeosurfaceVertShearDialog, self ).__init__() 
 
        self.geosurface_center = geosurface_center
         
        simpleshear_vertLayout = QGridLayout( )                            
                    
        simpleshear_vertLayout.addWidget( QLabel("Psi"), 0, 0, 1, 1 ) 
                    
        self.psi_QDSpinBox = QDoubleSpinBox()
        self.psi_QDSpinBox.setRange( 0.0, 89.9 )
        self.psi_QDSpinBox.setSingleStep( 0.1 )  
        simpleshear_vertLayout.addWidget( self.psi_QDSpinBox, 0, 1, 1, 1 )

        simpleshear_vertLayout.addWidget( QLabel("Alpha"), 0, 2, 1, 1 )             
        self.alpha_QDSpinBox = QDoubleSpinBox()
        self.alpha_QDSpinBox.setRange( 0.0, 359.9 )
        self.alpha_QDSpinBox.setSingleStep( 0.1 )  
        simpleshear_vertLayout.addWidget( self.alpha_QDSpinBox, 0, 3, 1, 1 )
        
                  
        simpleshear_vertLayout.addWidget( QLabel("Shear axis center"), 1, 0, 1, 2 )                  
 
        simpleshear_vertLayout.addWidget( QLabel("x"), 2, 0, 1, 1 ) 

        range_extreme = 9999999999 
        self.axis_center_x_QDSpinBox = QDoubleSpinBox()
        self.axis_center_x_QDSpinBox.setRange( -range_extreme, range_extreme )
        self.axis_center_x_QDSpinBox.setSingleStep( 0.1 )        
        simpleshear_vertLayout.addWidget( self.axis_center_x_QDSpinBox, 2, 1, 1, 1 )         

        simpleshear_vertLayout.addWidget( QLabel("y"), 2, 2, 1, 1 ) 

        self.axis_center_y_QDSpinBox = QDoubleSpinBox()
        self.axis_center_y_QDSpinBox.setRange( -range_extreme, range_extreme )
        self.axis_center_y_QDSpinBox.setSingleStep( 0.1 )        
        simpleshear_vertLayout.addWidget( self.axis_center_y_QDSpinBox, 2, 3, 1, 1 )   
        
        simpleshear_vertLayout.addWidget( QLabel("z"), 2, 4, 1, 1 ) 

        self.axis_center_z_QDSpinBox = QDoubleSpinBox()
        self.axis_center_z_QDSpinBox.setRange( -range_extreme, range_extreme )
        self.axis_center_z_QDSpinBox.setSingleStep( 0.1 )        
        simpleshear_vertLayout.addWidget( self.axis_center_z_QDSpinBox, 2, 5, 1, 1 )   
                                      
        self.axis_center_choice_QCheckBox = QCheckBox("fix shear axis center to geosurface center")
        self.axis_center_choice_QCheckBox.setChecked( True ) 
        self.axis_center_choice_QCheckBox.stateChanged.connect( self.set_center_values )
        simpleshear_vertLayout.addWidget( self.axis_center_choice_QCheckBox, 3, 0, 1, 4 )                             

        self.set_center_values( )

        done_QPushButton = QPushButton( "Apply" )
        done_QPushButton.clicked[bool].connect( self.vert_shear_done ) 
        done_QPushButton.setEnabled( True ) 
              
        simpleshear_vertLayout.addWidget( done_QPushButton, 4, 0, 1, 6 )
                                                                         
        self.setLayout( simpleshear_vertLayout )         
        self.adjustSize()                       
        self.setWindowTitle( 'Vertical simple shear' ) 
         

    def set_center_values( self ):

        if self.axis_center_choice_QCheckBox.isChecked():        
            self.axis_center_x_QDSpinBox.setValue( self.geosurface_center[0] ) 
            self.axis_center_y_QDSpinBox.setValue( self.geosurface_center[1] )        
            self.axis_center_z_QDSpinBox.setValue( self.geosurface_center[2] )
            
             
    def vert_shear_done( self, dummy_var ):        

        self.emit( SIGNAL( "update_geosurface_for_vert_shear" ) )                       
        self.close()
        
                   

                
def main():
    """
    Main of the module.
    """    
    app = QApplication(sys.argv)    
    form = GeosurfaceDeformationDialog()
    form.show()
    app.exec_()


main()       



