;FLAVOR:Marlin
;TIME:104
;Filament used: 0.320822m
;Layer height: 0.3
;MINX:101.5
;MINY:101.5
;MINZ:0.35
;MAXX:118.5
;MAXY:118.5
;MAXZ:2.15
;Generated with Cura_SteamEngine 4.12.1
M140 S80
M105
M190 S80
M104 S240
M105
M109 S240
M82 ;absolute extrusion mode
G28 ;Home
G1 Z15.0 F2000 ;Move the platform
G92 E0
G92 E0
G1 F1500 E-6.5
;LAYER_COUNT:7
;LAYER:0
M107
M204 S1000
;MESH:test.stl
G0 F7500 X118.5 Y118.5 Z0.35
;TYPE:WALL-OUTER
G1 F1500 E0
G1 F1146 X101.5 Y118.5 E7.42117
G1 X101.5 Y101.5 E14.84234
;LAYER:1
G1 F1500 E45.76493
M106 S85
;TYPE:WALL-OUTER
;MESH:test.stl
G1 F1500 E314.32184
M140 S0
M204 S500
M107
M104 S0
M140 S0
G92 E0
G1 E-10 F2000
G28 X0 Y0
M84
M82 ;absolute extrusion mode
M104 S0
;End of Gcode
;SETTING_3 {"global_quality": "[general]\\nversion = 4\\nname = Draft #2\\ndefin
;SETTING_3 ition = anet3d_a8\\n\\n[metadata]\\ntype = quality_changes\\nquality_
;SETTING_3 type = draft\\nsetting_version = 19\\n\\n[values]\\nadhesion_type = n
;SETTING_3 one\\nlayer_height = 0.3\\nlayer_height_0 = 0.35\\nmaterial_bed_tempe
;SETTING_3 rature = 80\\n\\n", "extruder_quality": ["[general]\\nversion = 4\\nn
;SETTING_3 ame = Draft #2\\ndefinition = anet3d_a8\\n\\n[metadata]\\ntype = qual
;SETTING_3 ity_changes\\nquality_type = draft\\nsetting_version = 19\\nposition 
;SETTING_3 = 0\\n\\n[values]\\nbottom_layers = 4\\ninfill_angles = [0, 20, 40, 6
;SETTING_3 0, 80, 100, 120, 140, 160 ]\\ninfill_line_distance = 4\\ninfill_patte
;SETTING_3 rn = lines\\ninfill_randomize_start_location = True\\nironing_only_hi
;SETTING_3 ghest_layer = True\\nironing_pattern = concentric\\nline_width = 3\\n
;SETTING_3 material_print_temperature = 240\\nretract_at_layer_change = True\\ns
;SETTING_3 kirt_line_count = 5\\ntop_layers = 4\\nwall_line_count = 3\\n\\n"]}
