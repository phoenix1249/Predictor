from  particule import Particule
import roblib
import time
import numpy as np
import sys
import matplotlib.pyplot as plt
from PyUnityVibes.UnityFigure import UnityFigure

class mission:
	def __init__(self, num):
		#Unity Display
		self.figure = UnityFigure(UnityFigure.FIGURE_3D, UnityFigure.SCENE_EMPTY)
		time.sleep(2)


		self.listParticules = [Particule(np.array([[0.0],[0.0],[0.0]]), np.array([[1.0],[0.0]]), np.diag((10**-9,10**-9,10**-9)), self.figure ) for i in range(num)]
		time.sleep(1)
		self.t = 0
		self.dt = 0.1
		self.tfinal = 60
		self.num = num
		self.anim = self.figure.createAnimation(self.dt)
		self.listboue = [[50,0],[25,25],[0,0]]

		time.sleep(1)

		print("Ajout des objets à l'animation")
		for part in self.listParticules:
			self.anim.addObject(part.auv)
			time.sleep(1.5)



		for coord in self.listboue:
			boue = self.figure.create(UnityFigure.OBJECT_3D_CUBE, coord[1], 0, coord[0], dimX=0.2, dimY=5, dimZ=0.2, color=UnityFigure.COLOR_BLACK)
			time.sleep(1.5)
			self.anim.addObject(boue)
			time.sleep(1.5)

	def __repr__(self):
		return "Programme de la mission: \n Aller en ligne droite, retour a 60s\n Nombre de particules {}".format(self.num)

	def display(self):
		print("Affichage de la mission sur PyUnityVibes")
		self.figure.animate(self.anim)




	def afficher_ellipse_all(self, fig, col=[0.9,0,0]):

		global max_x, max_y, min_y, min_x #pour regler la fenetre de l'affichage
		all_Xchap = [p.Xchap[0,0] for p in self.listParticules]
		all_Ychap = [p.Xchap[1,0] for p in self.listParticules]


		if min(all_Xchap) < min_x or min_x == None:
			min_x = min(all_Xchap)

		if min(all_Ychap) < min_y or min_y == None:
			min_y = min(all_Ychap)

		if max(all_Xchap) > max_x or max_x == None:
			max_x = max(all_Xchap)

		if max(all_Ychap) > max_y or max_y == None:
			max_y = max(all_Ychap)


		ax = fig.add_subplot(111, aspect='equal')
		ax.set_xlim(min_x-30, max_x+30)
		ax.set_ylim(min_y-30, max_y+30)
		for p in self.listParticules:
			p.afficher_ellipse(ax,col)



	def recalage(self):
		for part in self.listParticules:

			x_gps = part.X[0,0] + part.noise(0.48)
			y_gps = part.X[1,0] + part.noise(0.48)

			part.Xchap[0,0] = x_gps
			part.Xchap[1,0] = y_gps

			part.cov = np.diag([0.48**2, 0.48**2, part.cov[2,2]])

			L = amer[0] - part.Xchap[0,0]
			h = amer[1] - part.Xchap[1,0]

			part.theta = np.arctan2(h,L) #-(np.arctan2(h,L) + np.pi)
			part.U[1,0] = part.theta

	def aller_retour(self):

		global max_x, max_y, min_y, min_x   #pour regler la fenetre de l'affichage
		max_x, max_y, min_y, min_x = self.listParticules[0].Xchap[0,0], self.listParticules[0].Xchap[1,0], self.listParticules[0].Xchap[1,0], self.listParticules[0].Xchap[0,0]


		for part in self.listParticules:
			part.theta = np.arctan2(0.0001, 50)

		while self.t < self.tfinal :
			print("[{:.2f},{:.2f},{:.2f}]".format(self.listParticules[0].X[0,0], self.listParticules[0].X[1,0], self.listParticules[0].X[2,0]))
			sys.stdout.write("Aller  : t = %f \r" % self.t)
			for part in self.listParticules:
				part.step_aller_retour(self.t, self.dt)
				part.appendFrame(self.anim)
			self.t  += self.dt



		print(self.listParticules[0])
		self.recalage()
		print(self.listParticules[0])

		""" Affichage """
		fig_ellipse = plt.figure()
		self.afficher_ellipse_all(fig_ellipse, [0.9,0,0])



		self.recalage()

		while self.t < 2*self.tfinal:
			#sys.stdout.write("Retour : t = %f \r" % self.t)
			for part in self.listParticules:
				part.step_aller_retour(self.t, self.dt)
				part.appendFrame(self.anim)
			self.t  += self.dt

		print("\n Done ! ")
		time.sleep(1)
		self.display()


		""" Affichage """
		self.afficher_ellipse_all(fig_ellipse, [0,0,0.9])
		plt.xlabel("coordonnee x en metres")
		plt.ylabel("coordonnee y en metres")
		plt.title("Ellipses d'incertitude en position pour les differents\n auv apres trajet aller puis apres trajet retour")
		plt.show()


	def run(self):
		while self.t < self.tfinal :
			#sys.stdout.write("t = %f \r" % self.t)
			for part in self.listParticules:
				part.step_aller_retour(self.t, self.dt)
				part.appendFrame(self.anim)
			self.t  += self.dt

		print("\n Done ! ")
		time.sleep(1)
		self.display()

	def mission_triangle(self,liste_coord_amer):
		T = 0
		for amer in liste_coord_amer:
			T += self.listParticules[0].distance_amer(amer)
			print("T:",T)
			print("t:",self.t)
			print("amer :",amer)
			presence_amer = True
			theta_target = np.arctan2(amer[1] - self.listParticules[0].X[1,0],amer[0] - self.listParticules[0].X[0,0])
			print("theta_target",theta_target)
			#self.recalage(amer)
			while self.t < T:
				presence_amer = False
				#print(amer,"[{:.2f},{:.2f},{:.2f},{:.2f}]".format(self.listParticules[0].X[0,0], self.listParticules[0].X[1,0], self.listParticules[0].X[2,0],self.listParticules[0].theta))#print("[{:.2f},{:.2f},{:.2f}]".format(self.listParticules[0].X[0,0], self.listParticules[0].X[1,0], self.listParticules[0].X[2,0]))
				for part in self.listParticules:
					#part.theta = np.arctan2(amer[1] - part.X[1,0],amer[0] - part.X[0,0])
					part.step_mission(self.t, self.dt,presence_amer,amer,theta_target)
					part.appendFrame(self.anim)

				self.t += self.dt


		print("\n Done ! ")
		time.sleep(1)
		self.display()


if __name__=='__main__':
	N = 10
	mission = mission(N)
	mission.mission_triangle([[50,0],[25,25],[0,0]])
