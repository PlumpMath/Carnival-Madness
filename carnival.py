from math import pi, sin, cos
from direct.showbase.Transitions import Transitions
from pandac.PandaModules import loadPrcFileData
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.core import Filename, AmbientLight, DirectionalLight, PointLight, Spotlight
from panda3d.core import PandaNode,NodePath,Camera,TextNode, PerspectiveLens
from panda3d.core import Vec3, Vec4, BitMask32, VBase4, AudioSound, WindowProperties
from direct.interval.IntervalGlobal import Sequence, Parallel
from panda3d.core import Point3, CollisionPlane, Plane
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib
import sys, random
from direct.gui.DirectGui import *
from pandac.PandaModules import CollisionHandlerQueue, CollisionNode, CollisionSphere, CollisionTraverser
#import direct.directbase.DirectStart 
from direct.showbase.RandomNumGen import * 
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor
from panda3d.ai import *
 
START_BUT_TEXT = "PLAY"
EXIT_BUT_TEXT = "EXIT"
OPTION_BUT_TEXT = "PREFERENCES"
CREDITS_BUT_TEXT = "HIGH SCORES"
FULLSCREEN_BUT_TEXT = "Full Screen"
FULLSCREEN_LABEL = "Enable or Disable Full Screen"
SOUND_LABEL = "Enable or Disable Audio"
AUDIO_BUT_TEXT = "Sound"
GAME_OVER_LABEL = "ERRRR! THE MONSTER JUST NAILED YOU.\nYOUR SCORE : "
RESOLUTION_LABEL = "Screen Resolution Size"
LIGHT_BUT_TEXT = "Lights"
LIGHTS_LABEL = "Toggle Lights"
BACK_BUT_TEXT = "<--- BACK"
EXIT_TEXT = "Are you sure you would like to exit the game? All your progress would be lost?"
 
########################GAME STATES
STATE_RESET = 1
STATE_STARTED = 2
STATE_PREFS = 3
STATE_GAME_OVER = 4
STATE_PAUSED = 5
STATE_SCORE = 6
STATE_EXIT = 7 
 
#######################HEALTH VALUES
#Total Health - 100
#Lollipop - +2 
#Mint - +2
#GhostMode - No Collisions Applicable
 
class MyApp(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
		
		#Set background Image
		imageObject = OnscreenImage(parent = render2dp, image = 'image/nature.jpg', pos = (0, 0, 0), scale = 1)
		imageObject.setTransparency(TransparencyAttrib.MAlpha)
		base.cam2dp.node().getDisplayRegion(0).setSort(-20)
		#To show 2D text on Screen
		#textObject = OnscreenText(text = 'Carnival & Ralph!', pos = (0.1, 0.9), scale = 0.09, fg =( 1, 1, 1, 1), bg = (0.1,0.1,0.1, 1))
		#textObject = OnscreenText(text = '[Esc] To EXIT', pos = (-1, 0.9), scale = 0.06)
		#textObject = OnscreenText(text = '[V]To SWAP VIEW', pos = (-1, 0.80), scale = 0.06)
		#textObject = OnscreenText(text = '[Arrow Keys]To MOVE', pos = (-1, 0.70), scale = 0.06)
		#textObject = OnscreenText(text = '[L]toggle LIGHTS', pos = (-1, 0.60), scale = 0.06)
		#textObject = OnscreenText(text = '[E]USE', pos = (-1, 0.50), scale = 0.06)
		#To show the FPS
		loadPrcFileData('','show-frame-rate-meter 1')
				
		#Disable Camera change by mouse and hide mouse pointer, Set Full creen
		base.disableMouse()
		
		self.keyMap = {"left":0, "right":0, "forward":0, "back":0}
		self.worldView = False
		self.hasJet = False
		self.nearCarousel = False
		self.nearOctopus = False
		self.nearSkyride = False
		self.nearTent = False
		self.nearHouse = False
		self.nearCoaster = False
		self.nearLollipop = False
		self.lights = False
		self.pose = False
		self.nearBridge = False
		self.enableAudio = True
		self.screenResolutionVal = 4
		self.isFullScreen = False
		self.hasStarted = False
		self.hasResumed = False
		self.hasBoost = False
		self.boostCount = 1000
		self.curScore = 0
		self.ghostMode = False
		self.curState = STATE_RESET
	
		#These instance field shows health of character
		self.boyHealth = 100
		
		#self.loader.loadMusic('music/musicbox.ogg')
		self.song = self.loader.loadSfx("audio/horror.ogg")
		self.butHoverSound = self.loader.loadSfx("audio/but_hover.wav")
		#self.butClickSound = self.loader.loadSfx("audio/but_hover.wav")
		self.song.setVolume(0.5)
		
		#Load all the Models and Actors
		self.loadAllModels()
		
		######------>
		self.AIworld = AIWorld(self.render)
		self.AIchar = AICharacter("boy",self.monster, 150, 5, 150)
		self.AIworld.addAiChar(self.AIchar)
		self.AIbehaviors = self.AIchar.getAiBehaviors()
		#self.AIbehaviors.pathFollow(1.0)
		self.AIbehaviors.pursue(self.boy,1.0) 
		self.monster.loop("run")
		#self.AIbehaviors.addToPath(self.boy.getPos())
		#self.AIbehaviors.startFollow()
		
		#Set up the Collision Nodes 
		self.setupCollisionNodes()
		
		#Set initial Camera Distance from Ralph
		self.y = 30
		self.z = 13		
		
		#Start all the animations in the environment
		self.animatethings()
		
		#Add the task to move boy and rotate camera to get world View
		self.taskMgr.add(self.boyMoveTask, "BoyMoveTask")
		self.taskMgr.add(self.cameraLightCollisionTask, "cameraLightCollisionTask")
		
		#Write all the methods to be done when you press a key!
		self.accept("arrow_left", self.keys, ["left",1] )
		self.accept("arrow_right", self.keys, ["right",1])
		self.accept("arrow_up",self.keys, ["forward",1])
		self.accept("arrow_up-up",self.keys, ["forward", 0])
		self.accept("arrow_left-up",self.keys, ["left",0])
		self.accept("arrow_right-up",self.keys, ["right", 0])
		#self.accept("arrow_down-repeat", self.keys, ["right",1])
		#self.accept("arrow_down-up", self.keys, ["back", 0])
		#self.accept("arrow_down-up", self.stopWalk)
		#self.accept("arrow_up-up",self.stopWalk)
		#self.accept("arrow_left-up",self.stopWalk)
		#self.accept("arrow_right-up",self.stopWalk)
		#self.accept("v",self.switchView)
		self.accept("e",self.switchToJet)
		self.accept("escape", self.switchState, [STATE_STARTED, STATE_PAUSED])
		self.accept("l",self.changeLights)
		self.accept("wheel_up",self.keys, ["wheel_up",1])
		self.accept("wheel_down", self.keys, ["wheel_down",1])
		
		#Turn on ambient and directional Light for better graphics
		self.ambientLight = AmbientLight("ambientLight")
		self.ambientLight.setColor(Vec4(1, 1, 1, 1))
		self.sunLight = PointLight('plight')
		self.sunLight.setColor(VBase4(3, 3, 3, 1))
		self.sLight = self.render.attachNewNode(self.sunLight)
		self.sLight.setPos(350,300,150)
		
		
		#self.directionalLight = DirectionalLight("directionalLight")
		#self.directionalLight.setDirection(Vec3(-5, -5, -5))
		#self.directionalLight.setColor(Vec4(1, 1, 1, 1))
		#self.directionalLight.setSpecularColor(Vec4(1, 1, 1, 1))
		#self.dLight = self.render.attachNewNode(self.directionalLight)
		self.aLight = self.render.attachNewNode(self.ambientLight);
		self.hutLight = self.tent.attachNewNode(PointLight('tentLight'))
		self.hutLight.setPos(0,0,120)
		
		#Turn on the light effects and set world view for background of GUI
		self.switchView()
		self.changeLights()
		#self.resetState()
		
	def animatethings(self):
		
		seq1 = self.hawk.posInterval(4, Point3(250, 250, 50))
		seq3 = self.hawk.posInterval(4, Point3(-250, 250, 50))
		seq2 = self.hawk.hprInterval(0.1, Point3(80, 0, 0), startHpr = Point3(50, 0, 0))
		seq4 = self.hawk.hprInterval(0.1, Point3(70, 0, 0), startHpr = Point3(120, 0, 0))
		seq5 = self.hawk.posInterval(2, Point3(-100, 250, 30))
		seq6 = self.hawk.hprInterval(0.1, Point3(80, 0, 0), startHpr = Point3(50, 0, 0))
		seq7 = self.hawk.posInterval(4, Point3(250, 20, 20))
		seq8 = self.hawk.hprInterval(0.1, Point3(70, 0, 0), startHpr = Point3(120, 0, 0))
		seq9 = self.hawk.posInterval(4, Point3(0, 0, 100))
		seq = Sequence(seq1, seq2, seq3, seq4, seq5, seq6, seq7, seq8, seq9)
		seq.loop()
		#if not self.worldView:
			#seq.loop()
		#else:
			#if seq.isPlaying():
				#seq.pause()
		
		seq1 = self.hawk1.posInterval(4, Point3(-100, 50, 50))
		seq3 = self.hawk1.posInterval(4, Point3(-50, 250, 50))
		seq2 = self.hawk1.hprInterval(0.1, Point3(30, 0, 0), startHpr = Point3(50, 0, 0))
		seq4 = self.hawk1.hprInterval(0.1, Point3(90, 0, 0), startHpr = Point3(120, 0, 0))
		seq5 = self.hawk1.posInterval(2, Point3(-200, 150, 50))
		seq6 = self.hawk1.hprInterval(0.1, Point3(60, 0, 0), startHpr = Point3(50, 0, 0))
		seq7 = self.hawk1.posInterval(4, Point3(200, 200, 50))
		seq8 = self.hawk1.hprInterval(0.1, Point3(190, 0, 0), startHpr = Point3(120, 0, 0))
		seq9 = self.hawk1.posInterval(4, Point3(200, 0, 100))
		seq = Sequence(seq1, seq2, seq3, seq4, seq5, seq6, seq7, seq8, seq9)
		seq.loop()
		#if not self.worldView:
			#seq.loop()
		#else:
			#if seq.isPlaying():
				#seq.pause()
		
		seq1 = self.flamingo.posInterval(6, Point3(30, 70, 0))
		seq3 = self.flamingo.posInterval(2, Point3(70, 80, 0))
		seq2 = self.flamingo.hprInterval(2, Point3(-90, 0, 0), startHpr = Point3(0, 0, 0))
		seq4 = self.flamingo.hprInterval(0.1, Point3(-180, 0, 0), startHpr = Point3(-90, 0, 0))
		seq5 = self.flamingo.posInterval(2, Point3( 60, 50, 0))
		seq6 = self.flamingo.hprInterval(0.1, Point3(-270, 0, 0), startHpr = Point3(-180, 0, 0))
		seq7 = self.flamingo.posInterval(4, Point3(15, 50, 0))
		seq8 = self.flamingo.hprInterval(1, Point3( -180, 0, 0), startHpr = Point3(-270, 0, 0))
		seq9 = self.flamingo.posInterval(4, Point3(15, -10,0))
		seq10 = self.flamingo.hprInterval(1, Point3(-90, 0, 0), startHpr = Point3(-180, 0, 0))
		seq11 = self.flamingo.posInterval(4, Point3(30, -10, 0))
		seq12 = self.flamingo.hprInterval(1, Point3(0, 0, 0), startHpr = Point3(-90, 0, 0))
		seq = Sequence(seq1, seq2, seq3, seq4, seq5, seq6, seq7, seq8, seq9, seq10, seq11, seq12)
		seq.loop()
		#if not self.worldView:
			#seq.loop()
		#else:
			#if seq.isPlaying():
				#seq.pause()
		
		seq1 = self.blueBird.posInterval(8, Point3(-250, 200, 50))
		seq3 = self.blueBird.posInterval(8, Point3(-250, -200, 50))
		seq2 = self.blueBird.hprInterval(1, Point3(50, 0, 0), startHpr = Point3(0, 0, 0))
		seq4 = self.blueBird.hprInterval(1, Point3(30, 0, 0), startHpr = Point3(50, 0, 0))
		seq5 = self.blueBird.posInterval(5, Point3(-200, 150, 50))
		seq6 = self.blueBird.hprInterval(1, Point3(60, 0, 0), startHpr = Point3(50, 0, 0))
		seq7 = self.blueBird.posInterval(4, Point3(200, 200, 50))
		seq8 = self.blueBird.hprInterval(1, Point3(190, 0, 0), startHpr = Point3(120, 0, 0))
		seq9 = self.blueBird.posInterval(5, Point3(200, 0, 100))
		seq = Sequence(seq1, seq2, seq3, seq4, seq5, seq6, seq7, seq8, seq9)
		seq.loop()
		#if not self.worldView:
			#seq.loop()
		#else:
			#if seq.isPlaying():
				#seq.pause()
		
		seq1 = self.Dropship.posInterval(5, Point3(-130, -120, 40))
		seq2 = self.Dropship.posInterval(6, Point3(-130, 70, 40))
		seq3 = self.Dropship.posInterval(5, Point3(-130, 130, 13))
		seq4 = self.Dropship.hprInterval(3, Point3( 180, 0, 0), startHpr = Point3(0, 0, 0))
		seq5 = self.Dropship.posInterval(5, Point3(-130, 70, 40))
		seq6 = self.Dropship.posInterval(6, Point3(-130, -120, 40))
		seq7 = self.Dropship.posInterval(5, Point3(-130, -160, 13))
		seq8 = self.Dropship.hprInterval(3, Point3( 180, 0, 0), startHpr = Point3(0, 0, 0))
		self.skyRideSeq = Sequence(seq1, seq2, seq3, seq4, seq5, seq6, seq7, seq8)
		self.skyRideSeq.loop()
		#if not self.worldView:
			#self.skyRideSeq.loop()
		#else:
			#if self.skyRideSeq.isPlaying():
				#self.skyRideSeq.stop()
	
	def changeLights(self):
		if self.lights == False:
			self.render.setLight(self.aLight)
			self.render.setLight(self.sLight)
			#self.render.setLight(self.dLight)
			self.lights = True
		else:
			self.render.clearLight(self.aLight)
			self.render.clearLight(self.sLight)
			#self.render.clearLight(self.dLight)
			self.lights = False
		
	def climbOnJet(self):
		x = self.boy.getX(); y = self.boy.getY(); 
		x1 = self.jets.getX(); y1 = self.jets.getY(); 
		if self.hasJet:
			seq1 = self.boy.posInterval(1, Point3( x, y, 10))
			seq2 = self.jets.posInterval(1, Point3( 0, 0, 0))
			seq = Parallel(seq1, seq2)
			seq.start()
		else:
			seq1 = self.boy.posInterval(0.05, Point3( x, y, 15))
			par1 = self.boy.posInterval(0.5, Point3( x, y, 0))
			par2 = self.jets.posInterval(0.5, Point3( 0, -800, 350))
			seq = Sequence(seq1)
			seq.start()
			par = Parallel(par1, par2)
			par.start()
		return		
	      
	def switchToJet(self):
		if self.hasJet:
		      self.hasJet = False
		      self.climbOnJet()
		else:
		      self.jets.setScale(0.4)
		      self.hasJet = True
		      self.climbOnJet()
		return
	      
	def switchView(self):
		if self.worldView:
			taskMgr.remove("SpinCameraTask")
			self.worldView = False
			self.hasStarted = True
			self.hasResumed = True
			props = WindowProperties()
			props.setCursorHidden(True) 
			base.win.requestProperties(props)
			self.ambientLight.setColor(Vec4(.3, .3, .3, 1))
			#self.directionalLight.setDirection(Vec3(-5, -5, -5))
			
			self.startBut.hide(); self.exitBut.hide(); self.optionsBut.hide(); self.aboutBut.hide()
			self.transit.letterboxOff(2.5)
		else:
			taskMgr.add(self.spinCameraTask, "SpinCameraTask")
			self.worldView = True
			self.hasStarted = False
			self.hasResumed = False
			props = WindowProperties()
			props.setCursorHidden(False) 
			base.win.requestProperties(props)
			self.ambientLight.setColor(Vec4(.1, .1, .1, 1))
			#self.directionalLight.setDirection(Vec3( 5, 5, 5))	
			
			self.startBut.show(); self.exitBut.show(); self.optionsBut.show(); self.aboutBut.show()
			self.transit.letterboxOn(2.5)
			#Transitions(loader).fadeScreenColor(LVecBase4f(0.1,0.1,0.1,1))

	def spinCameraTask(self, task):
		angleDegrees = task.time * 6.0
		angleRadians = angleDegrees * (pi / 180.0)
		self.camera.setPos(320 * sin(angleRadians), -320.0 * cos(angleRadians), 30)
		self.camera.setHpr(angleDegrees, 0, 0)
		return Task.cont
	      
	def keys(self,action,args):
		#print action,args
	    #If camera goes away then Y should change faster while if it comes near then Z should change faster
		if action == "wheel_down":
			self.y = self.y - 2.5
			self.z = self.z - 5
			if self.y < 30:
				self.y = 30
			if self.z < 13:
				self.z = 13
		elif action == "wheel_up":
			self.y = self.y + 5
			self.z = self.z + 2
			if self.y > 160:
				self.y = 160
			if self.z > 50:
				self.z = 50
		if action == "forward":
			self.keyMap["forward"] = args
		if action == "right":
			self.keyMap["right"] = args
		if action == "left":
			self.keyMap["left"] = args
	      
	def cameraLightCollisionTask(self,task):
		base.camera.setPos(self.boy.getX(),self.boy.getY() - self.y, self.z)
		
		angleDegrees = task.time * 1.0
		angleRadians = angleDegrees * (pi / 180.0)
		self.sky.setHpr(angleDegrees, 0, 0)

		#Checks if we are near any of the rides inorder to create spatial awareness
		carouselDist = (self.boy.getPos() - self.carousel.getPos()).length()
		if carouselDist < 150 or carouselDist > -150:
				self.nearCarousel = True
		else:
				self.nearCarousel = False
		octopusDist = (self.boy.getPos() - self.octopus.getPos()).length()
		if octopusDist < 150 or octopusDist > -150:
				self.nearOctopus = True
		else:
				self.nearOctopus = False
		tentDist = (self.boy.getPos() - self.tent.getPos()).length()
		if tentDist < 150 or tentDist > -150:
				self.nearTent = True
		else:
				self.nearTent = False
		skyRideDist = (self.boy.getPos() - self.skyRide.getPos()).length()
		if skyRideDist < 150 or skyRideDist > -150:
				self.nearSkyride = True
		else:
				self.nearSkyride = False
		coasterDist = (self.boy.getPos() - self.coaster.getPos()).length()
		if coasterDist < 150 or coasterDist > -150:
				self.nearCoaster = True
		else:
				self.nearCoaster = False
		#print coasterDist
		
		if base.mouseWatcherNode.hasMouse() and self.curState == STATE_STARTED:
			base.camera.setH(-90 * base.mouseWatcherNode.getMouseX())
			base.camera.setP(45* base.mouseWatcherNode.getMouseY())
			#self.camera.setX(base.camera, -20 * globalClock.getDt())
		#if self.song.status() == AudioSound.BAD:
		#	print "BAD"
		#elif self.song.status() == AudioSound.READY:
		#	print "READY"
		#else:
		#	print "PLAYING"
		
		if self.nearCarousel:
			angleDegrees = task.time * 12.0
			angleRadians = angleDegrees * (pi / 180.0)
			self.carousel.setHpr(angleDegrees, 0, 0)
		if self.nearOctopus:
			angleDegrees = task.time * 12.0
			angleRadians = angleDegrees * (pi / 180.0)
			self.octopus.setHpr(angleDegrees, 0, 0)
		if self.nearTent:
			self.tent.setLight(self.hutLight)
		else:
			self.tent.clearLight(self.hutLight)
		if self.nearSkyride:
			self.skyRideSeq.pause()
		else:
			if not self.skyRideSeq.isPlaying():
				self.skyRideSeq.resume()
		if self.nearHouse:
			if not self.song.status() == AudioSound.PLAYING:
				if self.enableAudio:
					self.song.play()
			self.sfxManagerList[0].update()
		else:
			if self.song.status() == self.song.PLAYING:
				self.song.stop()
		# if self.nearCoaster:
			# #Do something
			# return
		if not self.nearBridge:
			self.boy.setZ(0)
			
		self.cTrav.traverse(render)
		self.collisionHandler1.sortEntries()
		if self.collisionHandler1.getNumEntries() == 0:
			self.startPos = self.boy.getPos()
			# self.nearCarousel = False
			# self.nearOctopus = False
			# self.nearSkyride = False
			# self.nearTent = False
			# self.nearHouse = False
			# self.nearBridge = False
			# #self.pose = False
			self.nearLollipop = False
		else:
			#self.nearBridge = False
			for i in range(self.collisionHandler1.getNumEntries()):
				entry = self.collisionHandler1.getEntry(i).getIntoNodePath().getName()
				#print entry
				# if "cCarouselNode" == self.collisionHandler1.getEntry(i).getIntoNodePath().getName():
					# self.nearCarousel = True
				# elif "cOctopusNode" == self.collisionHandler1.getEntry(i).getIntoNodePath().getName():
					# self.nearOctopus = True
				# elif "cTentNode" == self.collisionHandler1.getEntry(i).getIntoNodePath().getName():
					# self.nearTent = True
				# elif "cSkyrideNode1" == self.collisionHandler1.getEntry(i).getIntoNodePath().getName() or "cSkyrideNode2" == self.collisionHandler1.getEntry(i).getIntoNodePath().getName():
					# self.nearSkyride = True
				# elif "cHouseNode" == self.collisionHandler1.getEntry(i).getIntoNodePath().getName():
					# self.nearHouse = True
					
				if "Lollipop" == self.collisionHandler1.getEntry(i).getIntoNodePath().getName():
					print self.collisionHandler1.getEntry(i).getIntoNodePath(), self.collisionHandler1.getEntry(i).getInto()
					self.curScore += 1
					self.boyHealth = (self.boyHealth + 2)
					if self.boyHealth > 100:
						self.boyHealth = 100
					self.nearLollipop = True
				if "bridge" == self.collisionHandler1.getEntry(i).getIntoNodePath().getName():
					self.boy.setZ(self.collisionHandler1.getEntry(i).getSurfacePoint(self.render)[2] - 3)
					self.nearBridge = True
					#print self.collisionHandler1.getEntry(i).getSurfacePoint(self.bridge)
			if not (self.nearBridge or self.nearLollipop):
				self.boy.setPos(self.startPos)
		return Task.cont
		
###This method is used to change the health of actor which gets tired by running.
	def health(self):
		if self.isMoving:
			# self.countMonster=self.countMonster+1
			self.boyHealth = self.boyHealth - 0.5
			self.bar['value'] += self.boyHealth
			if self.boostCount > 0: 
				self.boostCount = self.boostCount - 1
			#print "self.boostCount = "+str(self.boostCount)
			print "self.boyHealth = "+str(self.boyHealth)
			
		else:
			#self.countMonster=self.countMonster-0.5
			if self.boyHealth < 100:
				self.boyHealth = self.boyHealth + 0.5
				self.bar['value'] += self.boyHealth
			if self.boostCount > 0: 
				self.boostCount = self.boostCount - 1
			#print "self.boostCount = "+str(self.boostCount)
			print "self.boyHealth = "+str(self.boyHealth)
			
		if self.boostCount == 0:
			self.hasBoost = False
		
		if (self.boyHealth < 0 or self.boyHealth == 0):
			self.switchState(STATE_STARTED, STATE_GAME_OVER)
		# if (self.countMonster == 0):
			# seq1 = self.monster.posInterval(2, Point3(0, 2, 5))
			# seq1.start()
			# self.monster.loop("run")
			# textObject = OnscreenText(text = 'Game Over Monster Killed You!!!', pos = (0, 0.50), scale = 0.1)
			# #self.switchView()
			#self.switchView()		
			
		# if (self.countMonster > 100):
			# seq1 = self.monster.posInterval(2, Point3(0, 20, 5))
			# seq1.start() 		
			
#These are the methods to move Ralph from his position as per the arrow keys
	def boyMoveTask(self, task):
		if self.curState == STATE_STARTED:
			self.health()
			if not self.hasBoost:
				if self.keyMap["forward"] != 0:
					self.boy.setY(self.boy, -35 * globalClock.getDt())
					self.isMoving = True
				if self.keyMap["left"] != 0:
					self.boy.setH(self.boy.getH() + 300 * globalClock.getDt())
					self.isMoving = True
				if self.keyMap["right"] != 0:
					self.boy.setH(self.boy.getH() - 300 * globalClock.getDt())
					self.isMoving = True
			else:
				if self.keyMap["forward"] != 0:
					self.boy.setY(self.boy, -70 * globalClock.getDt())
					self.isMoving = True
				if self.keyMap["left"] != 0:
					self.boy.setH(self.boy.getH() + 600 * globalClock.getDt())
					self.isMoving = True
				if self.keyMap["right"] != 0:
					self.boy.setH(self.boy.getH() - 600 * globalClock.getDt())
					self.isMoving = True
			if not (self.keyMap["forward"] or self.keyMap["left"] or self.keyMap["right"]):
				self.isMoving = False
			if self.isMoving:
				if not self.myAnimControl.isPlaying():
					self.boy.loop("run")
			else:
				self.boy.pose("walk", 5)
			
			#self.AIbehaviors.pursue(self.boy, 1.0)
			self.AIworld.update()
			self.monster.setZ(15)
			#if self.isMoving and not self.hasJet:
			#	if not self.myAnimControl.isPlaying():
			#		self.boy.loop("run")
				#self.AIbehaviors.addToPath(self.boy.getPos())
				#self.AIbehaviors.startFollow()
		#	if not self.isMoving:
		#		if self.rotateBack:
		#			self.boy.setH(self.boy.getH() + 10)
		#			if self.boy.getH() % 180 == 0:
		#				self.rotateBack = False
		#		elif self.rotateRight:
		#			self.boy.setH(self.boy.getH() + 10)
		#			if self.boy.getH() % 180 == 0:
		#				self.rotateRight = False
		#		elif self.rotateLeft:
		#			self.boy.setH(self.boy.getH() - 10)
		#			if self.boy.getH() % 180 == 0:
		#				self.rotateLeft = False
				#else:
				#	self.boy.pose("walk", 5)
			#self.health()
		return Task.again	
		
	def gameOverState(self):
		textObject = OnscreenText(text = 'Game Over You are out of Your health', pos = (0, 0.60), scale = 0.1)
		self.switchView()
		self.showGameOverMenu()
		self.hideMainMenu()
		
	def resetState(self):
		self.boy.setPos(5, -210, 0)
		self.monster.setPos(0,-325, 5)
		self.keyMap = {"left":0, "right":0, "forward":0, "back":0}
		self.worldView = True
		self.hasJet = False
		self.nearCarousel = False
		self.nearOctopus = False
		self.nearSkyride = False
		self.nearTent = False
		self.nearHouse = False
		self.nearCoaster = False
		self.nearLollipop = False
		self.lights = False
		self.pose = False
		self.nearBridge = False
		self.enableAudio = True
		self.screenResolutionVal = 4
		self.isFullScreen = False
		self.hasStarted = False
		self.hasResumed = False
		self.hasBoost = False
		self.boostCount = 1000
		self.curScore = 0
		self.ghostMode = False
		
		self.switchView()
		#These instance field counts distance b/w actor and monster while next one is health
		self.countMonster = 300
		self.boyHealth = 100
		#	for i in xrange(50):
		
	def keyUp(self):
		self.boy.setY(self.boy, -35 * globalClock.getDt())
		#self.boy.setY(self.boy.getY() + 2)
		self.isMoving = True
		#####------>
		#self.health()
	
	def keyDown(self):
		if not self.rotateBack:
			self.boy.setH(self.boy.getH() + 10)
			#base.camera.setH(self.boy.getH()+10)
			if self.boy.getH() % 180 == 0:
				self.rotateBack = True
		else:
			self.boy.setY(self.boy.getY() - 2)
			self.isMoving = True
			#####------>
			#self.health()
		
	def stopWalk(self):
		self.isMoving = False
		#####------>
		#self.health()
	
	def keyLeft(self):
		self.boy.setH(self.boy.getH() + 300 * globalClock.getDt())
		#if not self.rotateLeft:
		#	self.boy.setH(self.boy.getH() + 10)
		#	if self.boy.getH() % 90 == 0:
		#		self.rotateLeft = True
		#else:
		#	self.boy.setX(self.boy.getX() - 2)
		#	self.isMoving = True
			#####------>
		#	#self.health()
		
	def keyRight(self):
		self.boy.setH(self.boy.getH() - 300 * globalClock.getDt())
		#if not self.rotateRight:
		#	self.boy.setH(self.boy.getH() - 10)
		#	if self.boy.getH() % 90 == 0:
		#		self.rotateRight = True
		#else:
		#	self.boy.setX(self.boy.getX() + 2)
		#	self.isMoving = True
		#	#####------>
		#	#self.health()
	
	def hideMainMenu(self):
		self.startBut.hide()
		self.optionsBut.hide()
		self.exitBut.hide()
		self.aboutBut.hide()
		#self.switchView()
		#self.hasStarted = True
		#self.hasResumed = True
	
	def showMainMenu(self):
		self.startBut.show()
		self.optionsBut.show()
		self.exitBut.show()
		self.aboutBut.show()
		#self.hasResumed = False
		#self.hasStarted = False
	
	def showPrefs(self):
		#self.hideMainMenu()
		#self.labelResolution.show()
		self.labelFullScreen.show()
		self.labelSound.show()
		#self.resolutionSlider.show()
		self.fullScreenBut.show()
		self.backBut.show()
		self.audioBut.show()
		self.labelLights.show()
		self.lightsBut.show()
	
	def hidePrefs(self):
		#if self.isFullScreen:
			#props = WindowProperties()
			#if self.screenResolutionVal == 1:
				#props.setSize(1600, 900)
			#elif self.screenResolutionVal == 2:
				#props.setSize(1366, 768)
			#elif self.screenResolutionVal == 3:
				#props.setSize(1024, 768)
			#elif self.screenResolutionVal == 4:
				#props.setSize(800, 600)
			#props.setFullscreen(True)
			#base.win.requestProperties(props)
		#self.labelResolution.hide()
		self.labelFullScreen.hide()
		self.labelSound.hide()
		#self.resolutionSlider.hide()
		self.fullScreenBut.hide()
		self.audioBut.hide()
		self.backBut.hide()
		self.showMainMenu()
		self.labelLights.hide()
		self.lightsBut.hide()
		#self.hideGameOverMenu()
	
	def hideGameOverMenu(self):
		#self.showMainMenu()
		self.playAgainBut.hide()
		self.submitScore.hide()
		self.submitBut.hide()
		self.backBut1.hide()
		self.gameOverLabel.hide()
	
	def showGameOverMenu(self):
		self.playAgainBut.show()
		self.submitScore.show()
		self.submitBut.show()
		self.backBut1.show()
		self.gameOverLabel.show()
	
	def toggleLights(self,status):
		self.changeLights()
		
	def setResolution(self):
		if self.resolutionSlider['value']/25 == 4:
			self.screenResolutionVal = 4
			self.labelLights1['text'] = "Screen Resolution :- 1600 * 900"
		elif self.resolutionSlider['value']/25 == 3:
			self.screenResolutionVal = 3
			self.labelLights1['text'] = "Screen Resolution :- 1366 * 768"
		elif self.resolutionSlider['value']/25 == 2:
			self.screenResolutionVal = 2
			self.labelLights1['text'] = "Screen Resolution :- 1024 * 768"
		elif self.resolutionSlider['value']/25 == 1:
			self.screenResolutionVal = 1
			self.labelLights1['text'] = "Screen Resolution :- 800 * 600"
	
	def toggleScreen(self,status):
		props = WindowProperties()
		if not status:
			self.isFullScreen = False
			props.setFullscreen(False)
		else:
			self.isFullScreen = True
			props.setSize(1366, 768)
			props.setFullscreen(True)
		base.win.requestProperties(props)
		
	def toggleAudio(self,status):
		if not status:
			self.enableAudio = False
		else:
			self.enableAudio = True
			
	def setupCollisionNodes(self):
		#Collision Nodes are created here and attached to spheres
		self.cBoy = self.boy.attachNewNode(CollisionNode('cBoyNode'))
		self.cBoy.node().addSolid(CollisionSphere(0, 0, 3, 2.5))
		self.cStall = self.stall.attachNewNode(CollisionNode('cStallNode'))
		self.cStall.node().addSolid(CollisionSphere(0, 0, 0, 1.5))
		#self.cHouse = self.house.attachNewNode(CollisionNode('cHouseNode'))
		#self.cHouse.node().addSolid(CollisionSphere(0, 0, 0, 200))
		#self.cCarousel = self.carousel.attachNewNode(CollisionNode('cCarouselNode'))
		#self.cCarousel.node().addSolid(CollisionSphere(0, 0, 0, 30))
		#self.cOctopus = self.octopus.attachNewNode(CollisionNode('cOctopusNode'))
		#self.cOctopus.node().addSolid(CollisionSphere(0, 0, 0, 65))
		#self.cTent = self.tent.attachNewNode(CollisionNode('cTentNode'))
		#self.cTent.node().addSolid(CollisionSphere(0, 0, 0, 65))
		#self.cCoaster = self.coaster.attachNewNode(CollisionNode('cCoasterNode'))
		#self.cCoaster.node().addSolid(CollisionSphere(0, 0, 0, 170))
		self.cBridge = self.bridge.attachNewNode(CollisionNode('cBridge'))
		self.cBridge.node().addSolid(CollisionSphere(0, 0, 0, 25))
		self.cRingtoss = self.ringToss.attachNewNode(CollisionNode('cRingtoss'))
		self.cRingtoss.node().addSolid(CollisionSphere(0, 0, 0, 100))
		
		self.cSkyride1 = self.skyRide.attachNewNode(CollisionNode('cSkyrideNode1'))
		self.cSkyride1.node().addSolid(CollisionSphere(0, -250, 0, 40))
		
		self.cSkyride2 = self.skyRide.attachNewNode(CollisionNode('cSkyrideNode2'))
		self.cSkyride2.node().addSolid(CollisionSphere(0, 250, 0, 40))
		
		self.cPond = self.pGround.attachNewNode(CollisionNode('cPond'))
		self.cPond.node().addSolid(CollisionSphere(-50, 100, 0, 70))
		self.cPond1 = self.pGround.attachNewNode(CollisionNode('cPond1'))
		self.cPond1.node().addSolid(CollisionSphere(-220, -200, 0, 100))
		
		self.cFence = self.fence.attachNewNode(CollisionNode('cFence'))
		self.cFence.node().addSolid(CollisionPlane(Plane(Vec3(0, 1, 0), Point3(0, 0, 0))))
		self.cFence1 = self.fence1.attachNewNode(CollisionNode('cFence1'))
		self.cFence1.node().addSolid(CollisionPlane(Plane(Vec3(0, -1, 0), Point3(0, 0, 0))))
		self.cFence2 = self.fence2.attachNewNode(CollisionNode('cFence2'))
		self.cFence2.node().addSolid(CollisionPlane(Plane(Vec3(0, 1, 0), Point3(0, 0, 0))))
		self.cFence3 = self.fence3.attachNewNode(CollisionNode('cFence3'))
		self.cFence3.node().addSolid(CollisionPlane(Plane(Vec3(0, -1, 0), Point3(0, 0, 0))))
		#Uncomment this lines to see the collision spheres
		#self.cStall.show()
		#self.cHouse.show()
		#self.cCarousel.show()
		#self.cBoy.show()
		#self.cOctopus.show()
		#self.cCoaster.show()
		#self.cPond.show()
		#self.cPond1.show()
		#self.cFence.show()
		#self.cFence1.show()
		#self.cFence2.show()
		#self.cFence3.show()
		#self.cRingtoss.show()
		#self.cTent.show()
		#self.cSkyride1.show()
		#self.cSkyride2.show()
		
		self.cTrav=CollisionTraverser()
		self.collisionHandler1 = CollisionHandlerQueue()
		self.cTrav.addCollider(self.cBoy, self.collisionHandler1)
		
	def quit(self, args):
		if args:
			taskMgr.doMethodLater(2.6 ,sys.exit,'Exiting')
			self.transit.irisOut(2.5)
		else:
			self.askDialog.cleanup()
	
	def loadAllModels(self):
	  
		self.bar = DirectWaitBar(text = "", value = 100, pos = (0.9,0.4,0.8),scale = 0.3)
		#FadeIn the First Time when app starts
		self.transit = Transitions(loader)
		#self.transit.irisIn(2.5)
			
		#All the actors, models are loaded here 
		self.pGround = self.loader.loadModel("models/ParkGround")
		self.pGround.reparentTo(self.render)
		self.pGround.setPos(0,0,0)
		self.pGround.setScale(0.5,0.53,0.25)#(0.30, 0.30, 0.25)
		self.pGround.setHpr(180,0,0)
		
		self.fence = self.loader.loadModel("models/fence")
		self.fence.reparentTo(self.render)
		self.fence.setPos(355,-10,0)
		self.fence.setScale(55, 3, 2)
		self.fence.setHpr(90,0,0)
		self.fence1 = self.loader.loadModel("models/fence")
		self.fence1.reparentTo(self.render)
		self.fence1.setPos(-355,-10,0)
		self.fence1.setScale(55, 3, 2)
		self.fence1.setHpr(90,0,0)
		self.fence2 = self.loader.loadModel("models/fence")
		self.fence2.reparentTo(self.render)
		self.fence2.setPos(0,330,0)
		self.fence2.setScale(55, 3, 2)
		self.fence2.setHpr(180,0,0)
		self.fence3 = self.loader.loadModel("models/fence")
		self.fence3.reparentTo(self.render)
		self.fence3.setPos(180,-330,0)
		self.fence3.setScale(26, 3, 2)
		self.fence3.setHpr(180,0,0)
		self.fence4 = self.loader.loadModel("models/fence")
		self.fence4.reparentTo(self.render)
		self.fence4.setPos(-180,-330,0)
		self.fence4.setScale(26, 3, 2)
		self.fence4.setHpr(180,0,0)		
		
		self.gate = self.loader.loadModel("models/gate")
		self.gate.reparentTo(self.render)
		self.gate.setPos(0,-325,-5)
		self.gate.setScale(0.01, 0.02, 0.01)
		self.gate.setHpr(180,0,0)
		
		self.coaster = self.loader.loadModel("models/Coaster")
		self.coaster.reparentTo(self.render)
		self.coaster.setScale(0.3, 0.5, 0.5)
		self.coaster.setPos(-290, 50, 0)
		self.coaster.setHpr(270,0,0)
		
		self.fWheel = self.loader.loadModel("models/FerrisWheel")
		self.fWheel.reparentTo(self.render)
		self.fWheel.setScale(2.5, 2, 2)
		self.fWheel.setPos(310, -10, 1)
		self.fWheel.setHpr(100,0,0)
		
		self.tent = self.loader.loadModel("models/tent")
		self.tent.reparentTo(self.render)
		self.tent.setScale(1.2, 1.2, 0.9)
		self.tent.setPos(280, 260, 0)
		self.tent.setHpr(150,0,0)
		
		self.bridge = self.loader.loadModel("models/bridge")
		self.bridge.reparentTo(self.render)
		self.bridge.setScale(0.08,0.05,0.025)
		self.bridge.setPos(32,17,8)
		self.bridge.setHpr(180,0,0)
		
		self.carousel = self.loader.loadModel("models/Carousel")
		self.carousel.reparentTo(self.render)
		self.carousel.setScale(3, 3, 2)
		self.carousel.setPos(270, -270, 2)
		self.carousel.setHpr(180,0,0)
		
		self.smiley = self.loader.loadModel("models/smiley")
		self.smiley.reparentTo(self.carousel)
		self.smiley.setScale(2, 2, 2)
		self.smiley.setHpr(180, 0, 0)
		self.smiley.setPos(0, 0, 18)
		
		self.octopus = self.loader.loadModel("models/Octopus")
		self.octopus.reparentTo(self.render)
		self.octopus.setScale(1,1,1.5)
		self.octopus.setPos(-260,-270,1)
		self.octopus.setHpr(320,0,0)

		self.house = self.loader.loadModel("models/HauntedHouse")
		self.house.reparentTo(self.render)
		self.house.setScale(0.6,0.6,1.6)
		self.house.setPos(100,260,1)
		self.house.setHpr(180,0,0)
		
		self.stall = self.loader.loadModel("models/popcorncart")
		self.stall.reparentTo(self.render)
		self.stall.setScale(6,6,3)
		self.stall.setPos(20,-150,6)
		self.stall.setHpr(0,0,0)
		
		self.stallMan = self.loader.loadModel("models/Man")
		self.stallMan.reparentTo(self.render)
		self.stallMan.setScale(2.2,3.0,2.2)
		self.stallMan.setPos(15,-150,0)
		self.stallMan.setHpr(-90,0,0)
		
		self.stallWoman = self.loader.loadModel("models/Mana")
		self.stallWoman.reparentTo(self.render)
		self.stallWoman.setScale(2.5)
		self.stallWoman.setPos(28,-150,0)
		self.stallWoman.setHpr(90,0,0)
		
		self.stallGuy = self.loader.loadModel("models/RandomGuy")
		self.stallGuy.reparentTo(self.render)
		self.stallGuy.setScale(2.2,3.0,2.2)
		self.stallGuy.setPos(28,-145,0)
		self.stallGuy.setHpr(90,0,0)
		
		self.hawk = self.loader.loadModel("models/hawk")
		self.hawk.reparentTo(self.render)
		self.hawk.setScale(2,2,1)
		self.hawk.setPos(0, 0, 100)		
		self.hawk1 = self.loader.loadModel("models/hawk")
		self.hawk1.reparentTo(self.render)
		self.hawk1.setScale(2,2,1)
		self.hawk1.setPos(200, 0, 100)
		
		###-----
		self.Shrubbery = self.loader.loadModel("models/Shrubbery")
		self.Shrubbery.reparentTo(self.render)
		self.Shrubbery.setScale(0.01, 0.04, 0.01)
		self.Shrubbery.setPos(-28, 10, 0)
		self.Shrubbery.setHpr(0,0,0)
		self.Shrubbery1 = self.loader.loadModel("models/Shrubbery")
		self.Shrubbery1.reparentTo(self.render)
		self.Shrubbery1.setScale(0.01, 0.04, 0.01)
		self.Shrubbery1.setPos(-26, 30, 0)
		self.Shrubbery1.setHpr(0,0,0)
		self.Shrubbery2 = self.loader.loadModel("models/Shrubbery")
		self.Shrubbery2.reparentTo(self.render)
		self.Shrubbery2.setScale(0.01, 0.04, 0.01)
		self.Shrubbery2.setPos(-24, 20, 0)
		self.Shrubbery2.setHpr(0,0,0)
		self.Shrubbery3 = self.loader.loadModel("models/Shrubbery")
		self.Shrubbery3.reparentTo(self.render)
		self.Shrubbery3.setScale(0.01, 0.04, 0.01)
		self.Shrubbery3.setPos(60, 20, 0)
		self.Shrubbery3.setHpr(0,0,0)
		
		self.palmtree = self.loader.loadModel("models/palmtree")
		self.palmtree.reparentTo(self.render)
		self.palmtree.setScale(3, 3, 3)
		self.palmtree.setPos(-30, -60, 0)
		self.palmtree.setHpr(0,0,0)
		self.palmtree1 = self.loader.loadModel("models/palmtree")
		self.palmtree1.reparentTo(self.render)
		self.palmtree1.setScale(3, 3, 3)
		self.palmtree1.setPos(-55, -105, 0)
		self.palmtree2 = self.loader.loadModel("models/palmtree")
		self.palmtree2.reparentTo(self.render)
		self.palmtree2.setScale(3, 3, 3)
		self.palmtree2.setPos(-80, -70, 0)
		self.palmtree3 = self.loader.loadModel("models/palmtree")
		self.palmtree3.reparentTo(self.render)
		self.palmtree3.setScale(3, 3, 3)
		self.palmtree3.setPos(-60, -35, 0)
		self.palmtree4 = self.loader.loadModel("models/palmtree")
		self.palmtree4.reparentTo(self.render)
		self.palmtree4.setScale(3, 3, 3)
		self.palmtree4.setPos(-30, -30, 0)
		self.palmtree5 = self.loader.loadModel("models/palmtree")
		self.palmtree5.reparentTo(self.render)
		self.palmtree5.setScale(3, 3, 3)
		self.palmtree5.setPos(-30, -90, 0)
		
		self.pineTree = self.loader.loadModel("models/Pine_tree")
		self.pineTree.setScale(0.1)
		self.pineTree.reparentTo(self.render)
		self.pineTree.setPos(100, -160, 15)
		
		self.HappyTree = self.loader.loadModel("models/HappyTree")
		self.HappyTree.setScale(0.1)
		self.HappyTree.reparentTo(self.render)
		self.HappyTree.setPos(50, -100, 10)
		self.HappyTree.setHpr(10,0,0)
		
		self.HappyTree = self.loader.loadModel("models/HappyTree")
		self.HappyTree.setScale(0.1)
		self.HappyTree.reparentTo(self.render)
		self.HappyTree.setPos(180, -80, 10)
		self.HappyTree.setHpr(100,0,0)
		
		self.flamingo = self.loader.loadModel("models/flamingo")
		self.flamingo.reparentTo(self.render)
		self.flamingo.setScale(0.1, 0.1, 0.1)
		self.flamingo.setPos(30, -10, 1)
		self.flamingo.setHpr(0,0,0)
		
		self.lampPost = self.loader.loadModel("models/LampPost")
		self.lampPost.reparentTo(self.render)
		self.lampPost.setScale(2, 2, 2)
		self.lampPost.setPos(40, -185, 0)
		self.lampPost.setHpr(-30,0,0)
		self.lampPost1 = self.loader.loadModel("models/LampPost")
		self.lampPost1.reparentTo(self.render)
		self.lampPost1.setScale(2, 2, 2)
		self.lampPost1.setPos(25, -140, 0)
		self.lampPost1.setHpr(150,0,0)
		self.lampPost2 = self.loader.loadModel("models/LampPost")
		self.lampPost2.reparentTo(self.render)
		self.lampPost2.setScale(2, 2, 2)
		self.lampPost2.setPos(-10, -154, 0)
		self.lampPost2.setHpr(217,0,0)
		self.lampPost3 = self.loader.loadModel("models/LampPost")
		self.lampPost3.reparentTo(self.render)
		self.lampPost3.setScale(2, 2, 2)
		self.lampPost3.setPos(-10, -185, 0)
		self.lampPost3.setHpr(40,0,0)
		#self.lampPost.find("**/cLamp").node().setIntoCollideMask(BitMask32.bit(0))
		
		self.Oasis = self.loader.loadModel("models/oasis")
		self.Oasis.reparentTo(self.render)
		self.Oasis.setScale(0.04)
		self.Oasis.setPos(-280, 260, 0)
		self.Oasis.setHpr(-40,0,0)
		
		self.ringToss = self.loader.loadModel("models/ringtoss")
		self.ringToss.reparentTo(self.render)
		self.ringToss.setScale(0.3,0.3,0.5)
		self.ringToss.setPos(-270, -85, 0)
		self.ringToss.setHpr(90,0,0)
		
		self.RandomGuy = self.loader.loadModel("models/RandomGuy")
		self.RandomGuy.reparentTo(self.render)
		self.RandomGuy.setScale(2.5)
		self.RandomGuy.setPos(-235, -65, 0)
		self.RandomGuy.setHpr(180,0,0)
		
		self.RandomGirl1 = self.loader.loadModel("models/RandomGirl1")
		self.RandomGirl1.reparentTo(self.render)
		self.RandomGirl1.setScale(2.5)
		self.RandomGirl1.setPos(-235, -75, 0)
		self.RandomGirl1.setHpr(0,0,0)
		
		self.RandomGirl2 = self.loader.loadModel("models/RandomGirl2")
		self.RandomGirl2.reparentTo(self.render)
		self.RandomGirl2.setScale(2.5)
		self.RandomGirl2.setPos(-235, -85, 0)
		self.RandomGirl2.setHpr(180,0,0)
		
		self.RandomGirl3 = self.loader.loadModel("models/RandomGirl3")
		self.RandomGirl3.reparentTo(self.render)
		self.RandomGirl3.setScale(2.5)
		self.RandomGirl3.setPos(-235, -95, 0)
		self.RandomGirl3.setHpr(0,0,0)
		
		self.Kelly = self.loader.loadModel("models/Kelly")
		self.Kelly.reparentTo(self.render)
		self.Kelly.setScale(2.5)
		self.Kelly.setPos(-15, -155, 0)
		self.Kelly.setHpr(180,0,0)
		
		self.skyRide = self.loader.loadModel("models/Skyride")
		self.skyRide.reparentTo(self.render)
		self.skyRide.setScale(0.7,0.6,0.9)
		self.skyRide.setPos(-130, -20, 0)
		self.skyRide.setHpr(0,0,0)
		
		self.Dropship = self.loader.loadModel("models/Dropship")
		self.Dropship.reparentTo(self.render)
		self.Dropship.setScale(0.3)
		self.Dropship.setPos(-130, -160, 13)
		self.Dropship.setHpr(0,0,0)
		
		self.blueBird = self.loader.loadModel("models/bluebird")
		self.blueBird.reparentTo(self.render)
		self.blueBird.setScale(4)
		self.blueBird.setPos(200, 0, 100)	
		self.blueBird1 = self.loader.loadModel("models/bluebird")
		self.blueBird1.reparentTo(self.blueBird)
		self.blueBird1.setScale(1)
		self.blueBird1.setPos(3, -1, 0)
		self.blueBird2 = self.loader.loadModel("models/bluebird")
		self.blueBird2.reparentTo(self.blueBird)
		self.blueBird2.setScale(1)
		self.blueBird2.setPos(3, 1, 0)
		self.blueBird3 = self.loader.loadModel("models/bluebird")
		self.blueBird3.reparentTo(self.blueBird)
		self.blueBird3.setScale(1)
		self.blueBird3.setPos(6, -1, 0)
		self.blueBird4 = self.loader.loadModel("models/bluebird")
		self.blueBird4.reparentTo(self.blueBird)
		self.blueBird4.setScale(1)
		self.blueBird4.setPos(6, 1, 0)
		
		############
		self.sun = Actor("models/sun",{"shine":"models/sunrotate"})
		self.sun.reparentTo(self.render)
		self.sun.setScale(0.2)
		self.sun.setPos(350, 350, 150)
		self.sun.setHpr(90,0,0)
		self.sun.loop('shine')
		
		# dlight = DirectionalLight('dlight')
		# dlight.setColor(VBase4(1, 1, 1, 1))
		# dlnp = render.attachNewNode(dlight)
		# dlnp.setHpr(0, 0, 0)
		# self.sun.setLight(dlnp)
		
		self.trex = Actor("models/trex",{"eat":"models/trex-eat"})
		self.trex.reparentTo(self.render)
		self.trex.setScale(3)
		self.trex.setPos(-290, 245, 0)
		self.trex.setHpr(90,-10,0)
		self.trex.loop('eat')
		
		self.sky = self.loader.loadModel("models/skysphere")
		self.sky.reparentTo(self.render)
		self.sky.setScale(3)
		self.sky.setPos(0, 0, -30)
		self.sky.setHpr( -180, 0, 0)
		
		self.elephant = Actor("models/elephantmodel",{"fly":"models/elephantanimation"})
		self.elephant.reparentTo(self.render)
		self.elephant.setScale(0.3)
		self.elephant.setPos(50, 180, 100)
		self.elephant.setHpr(-60,20,0)
		self.elephant.loop('fly')
		seq1 = self.elephant.posInterval(40, Point3(-100, 250, 100))
		seq3 = self.elephant.posInterval(40, Point3(250, 200, 100))
		seq5 = self.elephant.posInterval(40, Point3(-200, 250, 100))
		seq9 = self.elephant.posInterval(40, Point3(50, 180, 100))
		seq = Sequence(seq1, seq3, seq5, seq9)
		seq.loop()
		
		self.gw01 = Actor("models/gw01",{"gw02":"models/gw02","gw03":"models/gw03","gw04":"models/gw04","gw05":"models/gw05","gw06":"models/gw06","gw07":"models/gw07","gw08":"models/gw08"})
		self.gw01.reparentTo(self.render)
		self.gw01.setScale(0.04)
		self.gw01.setPos(265, 180, 14)
		self.gw01.setHpr(-60,0,0)
		self.gw01.loop('gw02')
		self.gw01.loop('gw03')
		self.gw01.loop('gw04')
		self.gw01.loop('gw05')
		self.gw01.loop('gw06')
		self.gw01.loop('gw07')
		self.gw01.loop('gw08')
		self.bw01 = Actor("models/bw01",{"bw02":"models/bw02","bw03":"models/bw03"})
		self.bw01.reparentTo(self.render)
		self.bw01.setScale(0.04)
		self.bw01.setPos(215, 200, 14)
		self.bw01.setHpr(30,0,0)
		self.bw01.loop('bw02')
		self.bw01.loop('bw03')
		self.boymodel = Actor("models/boymodel",{"dance":"models/boyanimation"})
		self.boymodel.reparentTo(self.render)
		self.boymodel.setScale(0.015)
		self.boymodel.setPos(21, -150, 14)
		self.boymodel.setHpr(-60,20,0)
		self.boymodel.loop('dance')
		self.bromanactormodel = Actor("models/bromanactormodel",{"dance":"models/bromanactoranim","dance1":"models/bromanactoryeahanim"})
		self.bromanactormodel.reparentTo(self.render)
		self.bromanactormodel.setScale(4)
		self.bromanactormodel.setPos(150, -100, 7)
		self.bromanactormodel.setHpr(90,0,0)
		self.bromanactormodel.loop('dance')
		#self.bromanactormodel.play('dance1')
		self.bromancar = self.loader.loadModel("models/bromancar")
		self.bromancar.reparentTo(self.render)
		self.bromancar.setScale(4)
		self.bromancar.setPos(149, -100, 5)
		self.bromancar.setHpr(90,0,0)
		self.goose = Actor("models/goosemodel",{"goosefly":"models/gooseanimation"})
		self.goose.reparentTo(self.render)
		self.goose.setScale(0.5)
		self.goose.setPos(0, 100, 250)		
		self.goose.setHpr(50,0,0)
		self.goose.loop('goosefly')
		seq1 = self.goose.posInterval(20, Point3(2500, 2000, 250))
		seq2 = self.goose.posInterval(0, Point3(900, -100, 250))
		seq3 = self.goose.hprInterval(0, Point3(130, 0, 0), startHpr = Point3(0, 0, 0))
		seq4 = self.goose.posInterval(20, Point3(-1500, 2000, 250))
		seq5 = self.goose.posInterval(0, Point3(0, -100, 250))
		seq6 = self.goose.hprInterval(0, Point3(0, 0, 0), startHpr = Point3(130, 0, 0))
		seq = Sequence(seq1, seq2, seq3, seq4, seq5, seq6)
		seq.loop()
		
		self.lollipop = []
		for i in xrange(50):
			lollipop = self.loader.loadModel("models/lollipop")
			lollipop.reparentTo(self.render)
			lollipop.setScale(15)
			x = random.randint(-300,300)
			y = random.randint(-300,300)
			lollipop.setPos(x, y, 0)
			self.lollipop.append(lollipop)
		
		self.mint = []
		for i in xrange(50):
			mint = self.loader.loadModel("models/mint")
			mint.reparentTo(self.render)
			mint.setScale(15)
			x = random.randint(-300,300)
			y = random.randint(-300,300)
			mint.setPos(x, y, 5)
			self.mint.append(mint)
			mint.setR(90)
			mint.setH(90)

		# self.lollipop = self.loader.loadModel("models/lollipop")
		# self.lollipop.reparentTo(self.render)
		# self.lollipop.setScale(15)
		# self.lollipop.setPos(150, 150, 0)
		# self.lollipop1 = self.loader.loadModel("models/lollipop")
		# self.lollipop1.reparentTo(self.render)
		# self.lollipop1.setScale(15)
		# self.lollipop1.setPos(150, 320, 0)
		# self.lollipop2 = self.loader.loadModel("models/lollipop")
		# self.lollipop2.reparentTo(self.render)
		# self.lollipop2.setScale(15)
		# self.lollipop2.setPos(345, 40, 0)
		# self.lollipop3 = self.loader.loadModel("models/lollipop")
		# self.lollipop3.reparentTo(self.render)
		# self.lollipop3.setScale(15)
		# self.lollipop3.setPos(-280, -45, 0)
		# self.lollipop4 = self.loader.loadModel("models/lollipop")
		# self.lollipop4.reparentTo(self.render)
		# self.lollipop4.setScale(15)
		# self.lollipop4.setPos(-310, -90, 0)
		# self.lollipop5 = self.loader.loadModel("models/lollipop")
		# self.lollipop5.reparentTo(self.render)
		# self.lollipop5.setScale(15)
		# self.lollipop5.setPos(-325, -290, 0)
		# self.lollipop6 = self.loader.loadModel("models/lollipop")
		# self.lollipop6.reparentTo(self.render)
		# self.lollipop6.setScale(15)
		# self.lollipop6.setPos(350, 300, 0)
		# self.lollipop7 = self.loader.loadModel("models/lollipop")
		# self.lollipop7.reparentTo(self.render)
		# self.lollipop7.setScale(15)
		# self.lollipop7.setPos(-350, 100, 0)
		# self.lollipop8 = self.loader.loadModel("models/lollipop")
		# self.lollipop8.reparentTo(self.render)
		# self.lollipop8.setScale(15)
		# self.lollipop8.setPos(-300, 310, 0)
		# self.lollipop9 = self.loader.loadModel("models/lollipop")
		# self.lollipop9.reparentTo(self.render)
		# self.lollipop9.setScale(15)
		# self.lollipop9.setPos(20, -130, 0)
		# self.lollipop10 = self.loader.loadModel("models/lollipop")
		# self.lollipop10.reparentTo(self.render)
		# self.lollipop10.setScale(15)
		# self.lollipop10.setPos(40, 20, 10)
		# self.lollipop11 = self.loader.loadModel("models/lollipop")
		# self.lollipop11.reparentTo(self.render)
		# self.lollipop11.setScale(15)
		# self.lollipop11.setPos(340, -300, 0)
		# self.lollipop12 = self.loader.loadModel("models/lollipop")
		# self.lollipop12.reparentTo(self.render)
		# self.lollipop12.setScale(15)
		# self.lollipop12.setPos(-180, 200, 0)
		# self.lollipop13 = self.loader.loadModel("models/lollipop")
		# self.lollipop13.reparentTo(self.render)
		# self.lollipop13.setScale(15)
		# self.lollipop13.setPos(180, 200, 0)
		# self.lollipop14 = self.loader.loadModel("models/lollipop")
		# self.lollipop14.reparentTo(self.render)
		# self.lollipop14.setScale(15)
		# self.lollipop14.setPos(-144, -150, 0)
		
		# self.mint = self.loader.loadModel("models/mint")
		# self.mint.reparentTo(self.render)
		# self.mint.setScale(35)
		# self.mint.setPos(-114, -150, 3)
		# self.mint.setHpr(90, 0, 90)
		# self.mint1 = self.loader.loadModel("models/mint")
		# self.mint1.reparentTo(self.render)
		# self.mint1.setScale(35)
		# self.mint1.setPos(160, -80, 3)
		# self.mint1.setHpr(-30, 0, 90)
		# self.mint2 = self.loader.loadModel("models/mint")
		# self.mint2.reparentTo(self.render)
		# self.mint2.setScale(35)
		# self.mint2.setPos(340, -220, 3)
		# self.mint2.setHpr(90, 0, 90)
		# self.mint3 = self.loader.loadModel("models/mint")
		# self.mint3.reparentTo(self.render)
		# self.mint3.setScale(35)
		# self.mint3.setPos(-40, -40, 3)
		# self.mint3.setHpr(90, 0, 90)
		# self.mint4 = self.loader.loadModel("models/mint")
		# self.mint4.reparentTo(self.render)
		# self.mint4.setScale(35)
		# self.mint4.setPos(-32, 45, 3)
		# self.mint4.setHpr(0, 0, 90)
		# self.mint5 = self.loader.loadModel("models/mint")
		# self.mint5.reparentTo(self.render)
		# self.mint5.setScale(25)
		# self.mint5.setPos(255, 230, 3)
		# self.mint5.setHpr(90, 0, 90)
		# self.mint6 = self.loader.loadModel("models/mint")
		# self.mint6.reparentTo(self.render)
		# self.mint6.setScale(35)
		# self.mint6.setPos(320, 270, 3)
		# self.mint6.setHpr(90, 0, 90)
		# self.mint7 = self.loader.loadModel("models/mint")
		# self.mint7.reparentTo(self.render)
		# self.mint7.setScale(35)
		# self.mint7.setPos(190, 30, 3)
		# self.mint7.setHpr(0, 0, 90)
		# self.mint8 = self.loader.loadModel("models/mint")
		# self.mint8.reparentTo(self.render)
		# self.mint8.setScale(35)
		# self.mint8.setPos(-60, -240, 3)
		# self.mint8.setHpr(90, 0, 90)
		# self.mint9 = self.loader.loadModel("models/mint")
		# self.mint9.reparentTo(self.render)
		# self.mint9.setScale(35)
		# self.mint9.setPos(-160, 20, 3)
		# self.mint9.setHpr(90, 0, 90)
		# self.mint10 = self.loader.loadModel("models/mint")
		# self.mint10.reparentTo(self.render)
		# self.mint10.setScale(35)
		# self.mint10.setPos(30, -300, 3)
		# self.mint10.setHpr(90, 0, 90)
		
		self.boy = Actor("models/ralph",{"walk":"models/ralph-walk","run":"models/ralph-run"})
		self.boy.reparentTo(self.render)
		self.boy.setPos(5, -210, 0)
		self.boy.setScale(2, 2, 1.5)
		self.boy.setHpr(180, 0, 0)
		self.startPos = self.boy.getPos()
		self.isMoving = False
		self.rotateBack = False
		self.rotateLeft = False
		self.rotateRight = False
		self.myAnimControl = self.boy.getAnimControl('run')
		
		#####------>
		self.monster = Actor("models/monster1",{"run":"models/monster1-tentacle-attack"})
		self.monster.reparentTo(self.render)
		self.monster.setScale(3)
		self.monster.setPos(0,-325, 5)
		self.monster.setHpr(0, 180, 0)
			
		self.jets = self.loader.loadModel("models/GreenJumpJet")
		self.jets.reparentTo(self.boy)
		self.jets.setPos(0, 500, 10)
		self.jets.setZ(0)
		self.jets.setHpr(180,0,0)
		
		#Set up the main GUI Menu shown at the startup
		maps = loader.loadModel('models/button_maps')
		self.startBut = DirectButton(geom = (maps.find('**/but_steady'),maps.find('**/but_click'),maps.find('**/but_hover'),  maps.find('**/but_disable')), scale = 0.2, text = START_BUT_TEXT, text_scale = 0.2, pos = (0, 0, 0.3), rolloverSound = self.butHoverSound, clickSound = self.butHoverSound, command = self.switchState, extraArgs = [STATE_RESET, STATE_STARTED])
		self.exitBut = DirectButton(geom = (maps.find('**/but_steady'),maps.find('**/but_click'),maps.find('**/but_hover'),  maps.find('**/but_disable')), scale = 0.2, text = EXIT_BUT_TEXT, text_scale = 0.2, pos = (0, 0, -0.3), rolloverSound = self.butHoverSound, clickSound = self.butHoverSound, command = self.switchState, extraArgs = [STATE_PAUSED, STATE_EXIT])
		self.optionsBut = DirectButton(geom = (maps.find('**/but_steady'),maps.find('**/but_click'),maps.find('**/but_hover'),  maps.find('**/but_disable')), scale = 0.2, text = OPTION_BUT_TEXT, text_scale = 0.2, pos = (0, 0, 0.1), rolloverSound = self.butHoverSound, clickSound = self.butHoverSound, command = self.switchState, extraArgs = [STATE_RESET, STATE_PREFS])
		self.aboutBut = DirectButton(geom = (maps.find('**/but_steady'),maps.find('**/but_click'),maps.find('**/but_hover'),  maps.find('**/but_disable')), scale = 0.2, text = CREDITS_BUT_TEXT, text_scale = 0.2, pos = (0, 0, -0.1), rolloverSound = self.butHoverSound, clickSound = self.butHoverSound)
		
		#Set up the preferences GUI menu and then hide it
		self.labelFullScreen = DirectLabel(text = FULLSCREEN_LABEL, scale = 0.06, pos = (-0.9 , 0, 0.6))
		self.fullScreenBut = DirectCheckButton(geom = (maps.find('**/but_steady'),maps.find('**/but_click'),maps.find('**/but_hover'),  maps.find('**/but_disable')), scale = 0.15, text = FULLSCREEN_BUT_TEXT, text_scale = 0.3, pos = (0.7, 0, 0.6), rolloverSound = self.butHoverSound, clickSound = self.butHoverSound, indicatorValue = 0, command = self.toggleScreen)
		
		self.labelSound = DirectLabel(text = SOUND_LABEL, scale = 0.06, pos = (-0.9 , 0, 0.4))
		self.audioBut = DirectCheckButton(geom = (maps.find('**/but_steady'),maps.find('**/but_click'),maps.find('**/but_hover'),  maps.find('**/but_disable')), scale = 0.15, text = AUDIO_BUT_TEXT, text_scale = 0.3, pos = (0.7, 0, 0.4), rolloverSound = self.butHoverSound, clickSound = self.butHoverSound, indicatorValue = 0, command = self.toggleAudio)
		
		#self.resolutionSlider = DirectSlider(range = (0,100), value = 100, pageSize = 25, pos = (0.7, 0, 0), scale = 0.5, command = self.setResolution)
		#self.labelResolution = DirectLabel(text = RESOLUTION_LABEL, scale = 0.06, pos = (-0.9 , 0, 0))
		
		self.lightsBut = DirectCheckButton(geom = (maps.find('**/but_steady'),maps.find('**/but_click'),maps.find('**/but_hover'),  maps.find('**/but_disable')), scale = 0.15, text = LIGHT_BUT_TEXT, text_scale = 0.3, pos = (0.7, 0, 0.2), rolloverSound = self.butHoverSound, clickSound = self.butHoverSound, command = self.toggleLights, indicatorValue = 1)
		self.labelLights = DirectLabel(text = LIGHTS_LABEL, scale = 0.06, pos = (-0.9 , 0, 0.2))
		
		self.backBut = DirectButton(geom = (maps.find('**/but_steady'),maps.find('**/but_click'),maps.find('**/but_hover'),  maps.find('**/but_disable')), scale = (0.3,0.2,0.2), text = BACK_BUT_TEXT, text_scale = 0.3, pos = (0, 0, -0.4), rolloverSound = self.butHoverSound, clickSound = self.butHoverSound, command = self.switchState, extraArgs = [STATE_PREFS, STATE_RESET])

		
		self.gameOverLabel = DirectLabel(text = GAME_OVER_LABEL + str(self.curScore), scale = 0.1, pos = (-0.3 , 0, 0.6))
		self.submitScore = DirectEntry(text = "" , scale = (0.1, 0.07, 0.06),pos = (-1, 0, 0.3), initialText="Gamers call you?", numLines = 2,focus=1)		
		self.submitBut = DirectButton(geom = (maps.find('**/but_steady'),maps.find('**/but_click'),maps.find('**/but_hover'),  maps.find('**/but_disable')), scale = (0.2,0.2,0.2), text = "SUBMIT SCORE", text_scale = 0.2, pos = (0.8, 1, 0.3), rolloverSound = self.butHoverSound, clickSound = self.butHoverSound, command = self.hidePrefs)
		self.playAgainBut = DirectButton(geom = (maps.find('**/but_steady'),maps.find('**/but_click'),maps.find('**/but_hover'),  maps.find('**/but_disable')), scale = (0.2,0.2,0.2), text = "PLAY AGAIN", text_scale = 0.2, pos = (0, 1, 0), rolloverSound = self.butHoverSound, clickSound = self.butHoverSound, command = self.switchState, extraArgs = [STATE_GAME_OVER, STATE_STARTED])
		self.backBut1 = DirectButton(geom = (maps.find('**/but_steady'),maps.find('**/but_click'),maps.find('**/but_hover'),  maps.find('**/but_disable')), scale = (0.3,0.2,0.2), text = BACK_BUT_TEXT, text_scale = 0.3, pos = (0, 0, -0.4), rolloverSound = self.butHoverSound, clickSound = self.butHoverSound, command = self.switchState, extraArgs = [STATE_GAME_OVER, STATE_RESET])	
			
		self.hidePrefs()
		self.hideGameOverMenu()
				
	def switchState(self, curState, nextState):
		if curState == STATE_RESET and nextState == STATE_STARTED:
			self.hideMainMenu()
			taskMgr.remove("SpinCameraTask")
			props = WindowProperties()
			props.setCursorHidden(True) 
			base.win.requestProperties(props)
			self.ambientLight.setColor(Vec4(.3, .3, .3, 1))
			self.transit.letterboxOff(2.5)
		elif curState == STATE_RESET and nextState == STATE_PREFS: 
			self.hideMainMenu()
			self.showPrefs()
			
		#All these will be when current state is Prefs
		elif curState == STATE_PREFS and nextState == STATE_RESET:
			self.hidePrefs()
			self.showMainMenu()
		
		#All these will be when current state is started
		elif curState == STATE_STARTED and nextState == STATE_PAUSED:
			self.transit.letterboxOn(2.5)
			self.showMainMenu()
			self.optionsBut.hide()
			self.aboutBut.hide()
			self.optionsBut.hide()
			self.startBut['text'] = "RESUME GAME"
			props = WindowProperties()
			props.setCursorHidden(False) 
			base.win.requestProperties(props)
			taskMgr.add(self.spinCameraTask, "SpinCameraTask")
		elif curState == STATE_STARTED and nextState == STATE_GAME_OVER:
			self.showGameOverMenu()
			self.transit.letterboxOn(2.5)
			props = WindowProperties()
			props.setCursorHidden(False) 
			base.win.requestProperties(props)
		
		#All these will be when current state are Paused
		elif curState == STATE_PAUSED and nextState == STATE_STARTED:
			self.transit.letterboxOff(2.5)
			self.hideMainMenu()
			self.startBut['text'] = "PLAY"
			props = WindowProperties()
			props.setCursorHidden(True) 
			base.win.requestProperties(props)
			taskMgr.remove("SpinCameraTask")
		elif curState == STATE_PAUSED and nextState == STATE_EXIT:
			#maps = loader.loadModel('models/button_maps')
			#geomList = [(maps.find('**/but_steady'),maps.find('**/but_click'),maps.find('**/but_hover'),  maps.find('**/but_disable')), (maps.find('**/but_steady'),maps.find('**/but_click'),maps.find('**/but_hover'),  maps.find('**/but_disable')), (maps.find('**/but_steady'),maps.find('**/but_click'),maps.find('**/but_hover'),  maps.find('**/but_disable')), (maps.find('**/but_steady'),maps.find('**/but_click'),maps.find('**/but_hover'),  maps.find('**/but_disable'))]
			self.askDialog = YesNoDialog(dialogName="YesNoCancelDialog", text = EXIT_TEXT, buttonTextList = ["YES", "NO"], buttonSize = [-0.5,0.5,-0.05,0.1], fadeScreen = 1, command = self.quit)
		
		elif curState == STATE_GAME_OVER and nextState == STATE_STARTED:
			self.boy.setPos(5, -210, 0)
			self.monster.setPos(0,-325, 5)
			self.keyMap = {"left":0, "right":0, "forward":0, "back":0}
			self.hasJet = False
			self.nearCarousel = False
			self.nearOctopus = False
			self.nearSkyride = False
			self.nearTent = False
			self.nearHouse = False
			self.nearCoaster = False
			self.nearLollipop = False
			self.pose = False
			self.nearBridge = False
			self.hasBoost = False
			self.boostCount = 1000
			self.curScore = 0
			self.ghostMode = False
			self.countMonster = 300
			self.boyHealth = 100
			self.hideGameOverMenu()
		elif curState == STATE_GAME_OVER and nextState == STATE_RESET:
			self.boy.setPos(5, -210, 0)
			self.monster.setPos(0,-325, 5)
			self.keyMap = {"left":0, "right":0, "forward":0, "back":0}
			self.hasJet = False
			self.nearCarousel = False
			self.nearOctopus = False
			self.nearSkyride = False
			self.nearTent = False
			self.nearHouse = False
			self.nearCoaster = False
			self.nearLollipop = False
			self.pose = False
			self.nearBridge = False
			self.hasBoost = False
			self.boostCount = 1000
			self.curScore = 0
			self.ghostMode = False
			self.showMainMenu()
			self.hideGameOverMenu()
			
			self.countMonster = 300
			self.boyHealth = 100
			
		
		self.curState = nextState		
app = MyApp()
app.run()