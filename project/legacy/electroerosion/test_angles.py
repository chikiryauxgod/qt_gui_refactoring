import numpy as np
from robot import RobotState
from chain import my_chain

if __name__ == '__main__':
	s = RobotState()
	i = 0
	for x,y in zip(s.mins[:5], s.maxs[:5]):
		print(f"J{i}")
		my_chain.forward_kinematics([]) for j_pos in np.linspace(x, y, 50)
		i += 1


