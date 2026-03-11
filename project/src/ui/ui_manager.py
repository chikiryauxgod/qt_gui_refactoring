class UIManager:
    def __init__(self, erosion_tab, service_tab, state_manager):
        self.erosion_tab = erosion_tab
        self.service_tab = service_tab
        self.state = state_manager

    def sync_coordinates_to_tabs(self):
        for axis in ['X', 'Y', 'Z']:
            if axis in self.service_tab.xyz_controls:
                control = self.service_tab.xyz_controls[axis]
                value = getattr(self.state, f'current_{axis.lower()}')
                control['display'].setText(f"{value:.2f}")
                control['input'].setValue(value)
        if hasattr(self.service_tab, 'update_xyz_plot'):
            self.service_tab.update_xyz_plot()
        self.erosion_tab.x_control.value_label.setText(f"{self.state.current_x:.1f} мм")
        self.erosion_tab.y_control.value_label.setText(f"{self.state.current_y:.1f} мм")
        self.erosion_tab.z_control.value_label.setText(f"{self.state.current_z:.1f} мм")

    def sync_joints_to_tabs(self):
        for i, joint in enumerate(['J0', 'J1', 'J2', 'J3', 'J4', 'J5']):
            if joint in self.service_tab.joints_controls and i < len(self.state.current_joints):
                control = self.service_tab.joints_controls[joint]
                value = self.state.current_joints[i]
                control['display'].setText(f"{value:.2f}")
                control['input'].setValue(value)
        if hasattr(self.service_tab, 'update_joints_plot'):
            self.service_tab.update_joints_plot()
