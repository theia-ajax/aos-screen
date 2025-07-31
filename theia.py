from ctypes import *
import platform
import pygame

class TheiaLibSurface(Structure):
	_fields_ = [("flags", c_uint32),
			 	("format", c_uint32),
			 	("w", c_int32),
			 	("h", c_int32),
			 	("pitch", c_uint64),
			 	("pixels", c_void_p),
			 	("refcount", c_int),
			 	("reserved", c_void_p),
				]

(LOG_LEVEL_NONE,
 LOG_LEVEL_ERROR,
 LOG_LEVEL_WARNING,
 LOG_LEVEL_INFO,
 LOG_LEVEL_VERBOSE,
 LOG_LEVEL_DISABLED) = (0, 1, 2, 3, 4, 5)

def _load_theia_sim_lib():
	libname = './libtheia.so'
	if platform.system() == 'Windows':
		libname = 'theia'
		WinDLL("libgcc_s_seh-1.dll")
		WinDLL("SDL3.dll")
		
	lib = CDLL(libname)
	lib.Initialize.argtypes = [ c_int, c_char_p ]
	lib.StepSimulation.argtypes = [ c_float ]
	lib.RenderSimulationToFile.argtypes = [ c_char_p ]
	lib.RenderSimulationToSurface.restype = c_void_p
	lib.DestroyRenderedSurface.argtypes = [ c_void_p ]

	return lib

class _SimLib:
	def __init__(self, log_level, render_driver):
		self.lib = _load_theia_sim_lib()
		self.lib.Initialize(log_level, render_driver.encode('utf-8'))
	
	def __del__(self):
		self.lib.Shutdown()

	def step(self, dt):
		self.lib.StepSimulation(dt)
	
	def render(self):
		return SimRenderSurface(self.lib, self.lib.RenderSimulationToSurface())

class SimRenderSurface:
	def __init__(self, lib, surf):
		self.lib = lib
		self.surf_void_p = surf
	
	def __enter__(self):
		sim_surface = cast(self.surf_void_p, POINTER(TheiaLibSurface)).contents
		sim_surface_pixels_type = c_uint32 * sim_surface.w * sim_surface.h
		sim_surface_carray = sim_surface_pixels_type.from_address(sim_surface.pixels)
		sim_surface_bytes = memoryview(sim_surface_carray)
		return pygame.image.frombuffer(sim_surface_bytes, (sim_surface.w, sim_surface.h), "BGRA")

	def __exit__(self, type, value, traceback):
		self.lib.DestroyRenderedSurface(self.surf_void_p)

class SimRenderer:
	def __init__(self, log_level=LOG_LEVEL_WARNING, render_driver="vulkan", fps=60):
		self.fixed_delta_time = 1.0 / fps
		self.lib = _SimLib(log_level, render_driver)

	def next_frame(self):
		self.lib.step(self.fixed_delta_time)
		return self.lib.render()