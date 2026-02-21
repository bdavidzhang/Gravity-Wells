"""
Main game engine - handles game loop, input, and state management
Gravity Wells v2.0
"""

import pygame
import math
import random
import time
from game.physics import PhysicsEngine, Vector2D
from game.objects import Spaceship, Wormhole, BlackHole, ExplosionEffect, Starfield
from game.level import LevelManager

VERSION = "2.0"

class GameState:
    """Game state enumeration"""
    MENU = 0
    PLAYING = 1
    AIMING = 2
    FLYING = 3
    LEVEL_COMPLETE = 4
    GAME_OVER = 5
    LEVEL_SELECT = 6  # v2.0: Level select screen

class GameEngine:
    """Main game engine"""

    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Screen settings
        self.screen_width = 1024
        self.screen_height = 768
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption(f"Gravity Wells v{VERSION} - Spaceship Slingshotting Game")

        # Game components
        self.clock = pygame.time.Clock()
        self.physics = PhysicsEngine()
        self.level_manager = LevelManager()

        # Game state
        self.state = GameState.AIMING
        self.running = True
        self.spaceship = None
        self.current_level = None

        # Input handling
        self.mouse_pos = Vector2D(0, 0)
        self.mouse_pressed = False
        self.aim_start = Vector2D(0, 0)
        self.aim_power = 0

        # Dynamic aiming (like Angry Birds slingshot)
        self.aiming_active = False
        self.slingshot_base = Vector2D(0, 0)
        self.max_slingshot_distance = 120

        # UI settings
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 52)

        # v2.0: Starfield background
        self.starfield = Starfield(self.screen_width, self.screen_height)

        # v2.0: Screen shake system
        self.screen_shake_intensity = 0
        self.screen_shake_duration = 0
        self.screen_shake_timer = 0
        self.screen_offset = Vector2D(0, 0)

        # v2.0: Explosion effects
        self.explosions = []

        # v2.0: Time dilation near black holes
        self.time_dilation_factor = 1.0
        self.time_dilation_visual = 0  # For visual overlay

        # v2.0: Star rating display animation
        self.stars_earned = 0
        self.star_display_timer = 0

        # v2.0: Level select hover
        self.level_select_hover = -1

        # v2.0: Held keys for continuous thrust/brake
        self.keys_held = set()

        # v2.0: Transition timer for smooth state changes
        self.transition_timer = 0

        # Load first level
        self.load_current_level()

    def load_current_level(self):
        """Load the current level"""
        self.current_level = self.level_manager.get_current_level()
        if self.current_level:
            start_pos = self.current_level.spaceship_start
            self.spaceship = Spaceship(start_pos.x, start_pos.y)
            self.state = GameState.AIMING
            self.explosions = []
            self.time_dilation_factor = 1.0
            self.transition_timer = 0

            for obj in self.current_level.objects:
                if hasattr(obj, 'pulse_timer'):
                    obj.pulse_timer = 0

    def trigger_screen_shake(self, intensity=8, duration=0.3):
        """v2.0: Trigger screen shake effect"""
        self.screen_shake_intensity = intensity
        self.screen_shake_duration = duration
        self.screen_shake_timer = duration

    def handle_events(self):
        """Handle all input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                self.keys_held.add(event.key)
                self.handle_key_press(event.key)

            elif event.type == pygame.KEYUP:
                self.keys_held.discard(event.key)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_mouse_down()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.handle_mouse_up()

            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = Vector2D(event.pos[0], event.pos[1])

    def handle_key_press(self, key):
        """Handle keyboard input"""
        if key == pygame.K_r:
            if self.state != GameState.LEVEL_SELECT:
                self.restart_level()

        elif key == pygame.K_n:
            if self.state != GameState.LEVEL_SELECT:
                if self.level_manager.can_go_to_next_level():
                    if self.level_manager.next_level():
                        self.load_current_level()

        elif key == pygame.K_p:
            if self.state != GameState.LEVEL_SELECT:
                if self.level_manager.can_go_to_previous_level():
                    if self.level_manager.previous_level():
                        self.load_current_level()

        elif key == pygame.K_m:
            # v2.0: Toggle level select screen
            if self.state == GameState.LEVEL_SELECT:
                self.state = GameState.AIMING
                self.load_current_level()
            else:
                self.state = GameState.LEVEL_SELECT

        elif key == pygame.K_ESCAPE:
            if self.state == GameState.LEVEL_SELECT:
                self.state = GameState.AIMING
                self.load_current_level()
            else:
                self.running = False

    def handle_mouse_down(self):
        """Handle mouse button down"""
        if self.state == GameState.LEVEL_SELECT:
            self.handle_level_select_click()
            return

        if self.state == GameState.AIMING:
            mouse_to_ship = self.mouse_pos - self.spaceship.position
            if mouse_to_ship.magnitude() < 50:
                self.aiming_active = True
                self.mouse_pressed = True
                self.slingshot_base = Vector2D(self.spaceship.position.x, self.spaceship.position.y)

    def handle_mouse_up(self):
        """Handle mouse button up"""
        if self.state == GameState.AIMING and self.aiming_active:
            self.aiming_active = False
            self.mouse_pressed = False
            self.launch_spaceship()

    def handle_level_select_click(self):
        """v2.0: Handle clicks on the level select screen"""
        cols = 4
        cell_w = 200
        cell_h = 120
        start_x = (self.screen_width - cols * cell_w) // 2
        start_y = 140

        for i in range(len(self.level_manager.levels)):
            row = i // cols
            col = i % cols
            x = start_x + col * cell_w
            y = start_y + row * cell_h

            rect = pygame.Rect(x + 10, y + 10, cell_w - 20, cell_h - 20)
            if rect.collidepoint(self.mouse_pos.x, self.mouse_pos.y):
                if self.level_manager.is_level_unlocked(i):
                    self.level_manager.go_to_level(i)
                    self.load_current_level()
                break

    def launch_spaceship(self):
        """Launch the spaceship with calculated velocity from slingshot"""
        if self.spaceship and not self.spaceship.launched:
            slingshot_vector = self.slingshot_base - self.mouse_pos
            slingshot_distance = min(slingshot_vector.magnitude(), self.max_slingshot_distance)

            if slingshot_distance > 10:
                launch_direction = slingshot_vector.normalize()
                power_factor = slingshot_distance / self.max_slingshot_distance
                launch_velocity = launch_direction * power_factor * 350

                self.spaceship.launch(launch_velocity)
                self.state = GameState.FLYING
                self.current_level.shots_used += 1

    def update(self, dt):
        """Update game state"""
        # v2.0: Update starfield
        self.starfield.update(dt)

        # v2.0: Update screen shake
        if self.screen_shake_timer > 0:
            self.screen_shake_timer -= dt
            progress = self.screen_shake_timer / self.screen_shake_duration
            intensity = self.screen_shake_intensity * progress
            self.screen_offset = Vector2D(
                random.uniform(-intensity, intensity),
                random.uniform(-intensity, intensity)
            )
        else:
            self.screen_offset = Vector2D(0, 0)

        # v2.0: Update explosions
        for explosion in self.explosions[:]:
            explosion.update(dt)
            if not explosion.active:
                self.explosions.remove(explosion)

        # v2.0: Transition timer
        if self.transition_timer > 0:
            self.transition_timer -= dt

        if self.state == GameState.AIMING:
            self.update_aiming()

        elif self.state == GameState.FLYING:
            self.update_flying(dt)

        elif self.state == GameState.LEVEL_COMPLETE:
            self.star_display_timer += dt

        # Update level objects
        if self.current_level and self.state != GameState.LEVEL_SELECT:
            for obj in self.current_level.objects:
                if hasattr(obj, 'update'):
                    obj.update(dt)

    def update_aiming(self):
        """Update aiming state with dynamic slingshot"""
        if self.aiming_active and self.spaceship:
            slingshot_vector = self.slingshot_base - self.mouse_pos
            slingshot_distance = min(slingshot_vector.magnitude(), self.max_slingshot_distance)

            if slingshot_vector.magnitude() > self.max_slingshot_distance:
                constrained_direction = slingshot_vector.normalize()
                constrained_mouse_pos = self.slingshot_base - constrained_direction * self.max_slingshot_distance
                self.mouse_pos = constrained_mouse_pos

            if slingshot_distance > 10:
                launch_direction = slingshot_vector.normalize()
                power_factor = slingshot_distance / self.max_slingshot_distance
                predicted_velocity = launch_direction * power_factor * 350
                self.spaceship.velocity = predicted_velocity
                self.aim_power = power_factor * 3.0
            else:
                self.spaceship.velocity = Vector2D(0, 0)
                self.aim_power = 0

    def update_flying(self, dt):
        """Update flying state"""
        if self.spaceship and self.spaceship.launched:
            # v2.0: Calculate time dilation based on proximity to black holes
            self.time_dilation_factor = 1.0
            self.time_dilation_visual = 0
            if self.current_level:
                for obj in self.current_level.objects:
                    if isinstance(obj, BlackHole):
                        dist = (self.spaceship.position - obj.position).magnitude()
                        if dist < 200:
                            # Closer to black hole = stronger time dilation
                            dilation = max(0.3, dist / 200)
                            self.time_dilation_factor = min(self.time_dilation_factor, dilation)
                            self.time_dilation_visual = max(self.time_dilation_visual, 1.0 - dilation)

            # Apply time dilation to dt
            effective_dt = dt * self.time_dilation_factor

            # Update spaceship physics
            self.physics.update_object_physics(
                self.spaceship,
                self.current_level.gravity_sources,
                effective_dt
            )

            # Update spaceship
            self.spaceship.update(effective_dt)

            # Continuous thrust/brake while keys are held
            if self.spaceship.fuel > 0:
                if pygame.K_SPACE in self.keys_held:
                    if self.spaceship.velocity.magnitude() > 0:
                        thrust_dir = self.spaceship.velocity.normalize()
                    else:
                        thrust_dir = Vector2D(1, 0)
                    self.spaceship.use_thruster(thrust_dir, 30 * effective_dt * 10)
                if pygame.K_LSHIFT in self.keys_held or pygame.K_RSHIFT in self.keys_held:
                    if self.spaceship.velocity.magnitude() > 0:
                        brake_dir = self.spaceship.velocity.normalize() * -1
                        self.spaceship.use_thruster(brake_dir, 25 * effective_dt * 10)

            # v2.0: Check wormhole collisions
            self.check_wormhole_collisions()

            # Check collisions
            self.check_collisions()

            # Screen wrapping: ship reappears on the opposite side
            margin = 20
            if self.spaceship.position.x < -margin:
                self.spaceship.position.x = self.screen_width + margin
            elif self.spaceship.position.x > self.screen_width + margin:
                self.spaceship.position.x = -margin
            if self.spaceship.position.y < -margin:
                self.spaceship.position.y = self.screen_height + margin
            elif self.spaceship.position.y > self.screen_height + margin:
                self.spaceship.position.y = -margin

    def check_wormhole_collisions(self):
        """v2.0: Check if spaceship enters a wormhole"""
        if not self.spaceship or not self.spaceship.launched or not self.current_level:
            return

        for obj in self.current_level.wormholes:
            if isinstance(obj, Wormhole) and obj.cooldown <= 0:
                dist = (self.spaceship.position - obj.position).magnitude()
                if dist < obj.radius + self.spaceship.radius:
                    if obj.teleport(self.spaceship):
                        self.trigger_screen_shake(6, 0.2)
                        break

    def check_collisions(self):
        """Check for collisions between spaceship and objects"""
        if not self.spaceship or not self.spaceship.launched:
            return

        for obj in self.current_level.objects:
            # Skip wormholes (handled separately)
            if isinstance(obj, Wormhole):
                continue

            if self.spaceship.collides_with(obj):
                if isinstance(obj, type(self.current_level.goal)) and obj == self.current_level.goal:
                    # Level completed!
                    self.stars_earned = self.level_manager.complete_level(
                        self.level_manager.current_level_index,
                        self.current_level.shots_used,
                        self.current_level.max_shots
                    )
                    self.star_display_timer = 0
                    self.state = GameState.LEVEL_COMPLETE
                    self.trigger_screen_shake(4, 0.2)
                    break
                else:
                    # Hit obstacle or planet - explosion and reset
                    self.spawn_explosion(
                        self.spaceship.position.x,
                        self.spaceship.position.y
                    )
                    self.trigger_screen_shake(10, 0.4)
                    self.reset_for_next_shot()
                    break

    def spawn_explosion(self, x, y, color=(0, 255, 255)):
        """v2.0: Create explosion effect at position"""
        self.explosions.append(ExplosionEffect(x, y, color))

    def reset_for_next_shot(self):
        """Reset spaceship for next shot"""
        if self.current_level.shots_used >= self.current_level.max_shots:
            self.state = GameState.GAME_OVER
            self.trigger_screen_shake(12, 0.5)
        else:
            start_pos = self.current_level.spaceship_start
            self.spaceship = Spaceship(start_pos.x, start_pos.y)
            self.state = GameState.AIMING
            self.time_dilation_factor = 1.0
            self.time_dilation_visual = 0

    def restart_level(self):
        """Restart the current level"""
        self.level_manager.restart_level()
        self.load_current_level()

    def draw(self):
        """Render everything to screen"""
        # Clear screen with deep space background
        self.screen.fill((2, 0, 15))

        # v2.0: Draw animated starfield
        self.starfield.draw(self.screen)

        # Create offset surface for screen shake
        offset_x = int(self.screen_offset.x)
        offset_y = int(self.screen_offset.y)

        if self.state == GameState.LEVEL_SELECT:
            self.draw_level_select()
        else:
            # Draw level objects
            if self.current_level:
                for obj in self.current_level.objects:
                    obj.draw(self.screen)

            # Draw spaceship
            if self.spaceship:
                self.spaceship.draw(self.screen)

            # Draw trajectory prediction when aiming
            if self.state == GameState.AIMING and self.spaceship and self.aim_power > 0.1:
                self.draw_trajectory_prediction()

            # Draw slingshot when aiming
            if self.state == GameState.AIMING and self.aiming_active:
                self.draw_slingshot()

            # v2.0: Draw explosions
            for explosion in self.explosions:
                explosion.draw(self.screen)

            # v2.0: Draw time dilation overlay
            if self.time_dilation_visual > 0.1:
                self.draw_time_dilation_overlay()

            # Draw UI
            self.draw_ui()

            # Draw gravity information
            self.draw_gravity_info()

        # Update display
        pygame.display.flip()

    def draw_time_dilation_overlay(self):
        """v2.0: Draw visual effect for time dilation near black holes"""
        intensity = self.time_dilation_visual
        # Draw vignette-like darkening at edges
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)

        # Purple-ish time distortion tint
        alpha = int(60 * intensity)
        overlay.fill((40, 0, 80, alpha))
        self.screen.blit(overlay, (0, 0))

        # Draw "TIME DILATING" text when strong
        if intensity > 0.3:
            pulse = abs(math.sin(time.time() * 4))
            alpha_text = int(200 * intensity * pulse)
            color = (150, 100, 255)
            text = self.small_font.render("[ TIME DILATION ]", True, color)
            text.set_alpha(alpha_text)
            rect = text.get_rect(center=(self.screen_width // 2, 50))
            self.screen.blit(text, rect)

    def draw_thrust_hud(self):
        """Draw boost/brake indicators during flight"""
        if not self.spaceship:
            return

        boosting = pygame.K_SPACE in self.keys_held and self.spaceship.fuel > 0
        braking = (pygame.K_LSHIFT in self.keys_held or pygame.K_RSHIFT in self.keys_held) and self.spaceship.fuel > 0
        has_fuel = self.spaceship.fuel > 0

        hud_x = self.screen_width - 220
        hud_y = self.screen_height - 90

        # Background panel
        panel = pygame.Rect(hud_x - 10, hud_y - 8, 220, 75)
        panel_surface = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 120))
        self.screen.blit(panel_surface, (panel.x, panel.y))
        pygame.draw.rect(self.screen, (60, 60, 100), panel, 1)

        # Fuel bar
        fuel_ratio = self.spaceship.fuel / self.spaceship.max_fuel
        bar_w = 200
        bar_h = 10
        fuel_color = (int(255 * (1 - fuel_ratio)), int(255 * fuel_ratio), 80)
        pygame.draw.rect(self.screen, (30, 30, 40), (hud_x, hud_y, bar_w, bar_h))
        pygame.draw.rect(self.screen, fuel_color, (hud_x, hud_y, int(bar_w * fuel_ratio), bar_h))
        fuel_label = self.small_font.render(f"Fuel: {self.spaceship.fuel}", True, (200, 200, 200))
        self.screen.blit(fuel_label, (hud_x, hud_y - 6))

        # Boost indicator
        boost_y = hud_y + 18
        if boosting:
            boost_color = (100, 255, 200)
            boost_text = ">> BOOST [SPACE] <<"
            # Active glow
            pulse = abs(math.sin(time.time() * 8)) * 0.3 + 0.7
            glow_color = (0, int(200 * pulse), int(100 * pulse))
            pygame.draw.rect(self.screen, glow_color, (hud_x - 2, boost_y, 104, 18), 1)
        elif has_fuel:
            boost_color = (120, 180, 150)
            boost_text = "   BOOST [SPACE]"
        else:
            boost_color = (80, 80, 80)
            boost_text = "   BOOST [NO FUEL]"
        boost_surface = self.small_font.render(boost_text, True, boost_color)
        self.screen.blit(boost_surface, (hud_x, boost_y))

        # Brake indicator
        brake_y = hud_y + 38
        if braking:
            brake_color = (255, 150, 100)
            brake_text = ">> BRAKE [SHIFT] <<"
            pulse = abs(math.sin(time.time() * 8)) * 0.3 + 0.7
            glow_color = (int(200 * pulse), int(80 * pulse), 0)
            pygame.draw.rect(self.screen, glow_color, (hud_x - 2, brake_y, 104, 18), 1)
        elif has_fuel:
            brake_color = (180, 140, 120)
            brake_text = "   BRAKE [SHIFT]"
        else:
            brake_color = (80, 80, 80)
            brake_text = "   BRAKE [NO FUEL]"
        brake_surface = self.small_font.render(brake_text, True, brake_color)
        self.screen.blit(brake_surface, (hud_x, brake_y))

    def draw_trajectory_prediction(self):
        """Draw predicted trajectory with enhanced visual effects"""
        if self.spaceship and self.spaceship.velocity.magnitude() > 0:
            trajectory = self.physics.predict_trajectory(
                self.spaceship.position,
                self.spaceship.velocity,
                self.spaceship.mass,
                self.current_level.gravity_sources,
                steps=60,
                dt=0.15
            )

            for i, point in enumerate(trajectory[::2]):
                progress = 1.0 - (i / len(trajectory))

                color = (
                    int(100 + 155 * progress),
                    int(255 * progress),
                    int(255)
                )

                size = max(1, int(4 * progress))
                pygame.draw.circle(self.screen, color, (int(point[0]), int(point[1])), size)

    def draw_slingshot(self):
        """Draw the slingshot aiming mechanism like Angry Birds"""
        if not self.spaceship or not self.aiming_active:
            return

        slingshot_vector = self.slingshot_base - self.mouse_pos
        slingshot_distance = min(slingshot_vector.magnitude(), self.max_slingshot_distance)

        if slingshot_distance > 5:
            band_offset = 8
            perpendicular = Vector2D(-slingshot_vector.y, slingshot_vector.x).normalize() * band_offset

            # Left band
            left_anchor = self.slingshot_base + perpendicular
            pygame.draw.line(self.screen, (139, 69, 19),
                           left_anchor.to_tuple(),
                           self.mouse_pos.to_tuple(), 4)

            # Right band
            right_anchor = self.slingshot_base - perpendicular
            pygame.draw.line(self.screen, (139, 69, 19),
                           right_anchor.to_tuple(),
                           self.mouse_pos.to_tuple(), 4)

            # Power indicator color
            power_ratio = slingshot_distance / self.max_slingshot_distance
            if power_ratio < 0.3:
                power_color = (0, 255, 100)
            elif power_ratio < 0.7:
                power_color = (255, 200, 0)
            else:
                power_color = (255, 50, 50)

            # Aiming line showing launch direction
            launch_direction = slingshot_vector.normalize()
            aim_end = self.slingshot_base + launch_direction * 60
            pygame.draw.line(self.screen, power_color,
                           self.slingshot_base.to_tuple(),
                           aim_end.to_tuple(), 3)

            # Arrow head
            pygame.draw.circle(self.screen, power_color,
                             (int(aim_end.x), int(aim_end.y)), 4)

            # Pull-back indicator
            pygame.draw.circle(self.screen, (255, 255, 255),
                             (int(self.mouse_pos.x), int(self.mouse_pos.y)), 6, 2)

            # Power meter
            power_bar_length = int(power_ratio * 50)
            power_bar_start = self.slingshot_base + Vector2D(20, -10)

            # Background of power meter
            pygame.draw.rect(self.screen, (50, 50, 50),
                           (power_bar_start.x, power_bar_start.y, 50, 8))

            # Power meter fill
            if power_bar_length > 0:
                pygame.draw.rect(self.screen, power_color,
                               (power_bar_start.x, power_bar_start.y, power_bar_length, 8))

    def draw_stars(self, x, y, count, size=16):
        """v2.0: Draw star rating icons"""
        for i in range(3):
            star_x = x + i * (size + 4)
            if i < count:
                # Filled star - golden yellow
                color = (255, 215, 0)
                self.draw_star_shape(star_x, y, size // 2, color)
            else:
                # Empty star - dark outline
                color = (80, 80, 80)
                self.draw_star_shape(star_x, y, size // 2, color, filled=False)

    def draw_star_shape(self, cx, cy, radius, color, filled=True):
        """Draw a 5-pointed star shape"""
        points = []
        for i in range(10):
            angle = math.radians(i * 36 - 90)
            r = radius if i % 2 == 0 else radius * 0.4
            px = cx + math.cos(angle) * r
            py = cy + math.sin(angle) * r
            points.append((int(px), int(py)))

        if filled:
            pygame.draw.polygon(self.screen, color, points)
        pygame.draw.polygon(self.screen, color, points, 2)

    def draw_ui(self):
        """Draw enhanced user interface v2.0"""
        if self.current_level:
            progress = self.level_manager.get_level_progress()

            # v2.0: Version badge
            version_text = f"v{VERSION}"
            version_surface = self.small_font.render(version_text, True, (80, 80, 120))
            self.screen.blit(version_surface, (self.screen_width - 50, 10))

            # Level info
            level_text = f"Level {progress['current']}/{progress['total']}: {progress['name']}"
            if progress['is_completed']:
                level_color = (100, 255, 100)
            else:
                level_color = (100, 255, 255)

            text_surface = self.font.render(level_text, True, level_color)
            self.screen.blit(text_surface, (10, 10))

            # v2.0: Star progress
            stars_text = f"Stars: {progress['total_stars']}/{progress['max_stars']}"
            stars_surface = self.small_font.render(stars_text, True, (255, 215, 0))
            self.screen.blit(stars_surface, (10, 40))

            # v2.0: Current level stars
            current_stars = progress['current_stars']
            if current_stars > 0:
                self.draw_stars(140, 33, current_stars, 14)

            # Progress summary
            progress_text = f"Completed: {progress['completed_count']}/{progress['total']} | Unlocked: {progress['unlocked_count']}/{progress['total']}"
            progress_surface = self.small_font.render(progress_text, True, (200, 200, 255))
            self.screen.blit(progress_surface, (10, 58))

            # Shots info with color coding
            shots_text = f"Shots: {self.current_level.shots_used}/{self.current_level.max_shots}"
            if self.current_level.shots_used >= self.current_level.max_shots:
                shots_color = (255, 100, 100)
            elif self.current_level.shots_used >= self.current_level.max_shots - 1:
                shots_color = (255, 255, 100)
            else:
                shots_color = (100, 255, 100)

            shots_surface = self.small_font.render(shots_text, True, shots_color)
            self.screen.blit(shots_surface, (10, 82))

            # Fuel info
            if self.spaceship:
                fuel_ratio = self.spaceship.fuel / self.spaceship.max_fuel
                fuel_color = (
                    int(255 * (1 - fuel_ratio)),
                    int(255 * fuel_ratio),
                    100
                )
                fuel_text = f"Fuel: {self.spaceship.fuel}/{self.spaceship.max_fuel}"
                fuel_surface = self.small_font.render(fuel_text, True, fuel_color)
                self.screen.blit(fuel_surface, (10, 106))

        # Game state messages
        if self.state == GameState.LEVEL_COMPLETE:
            self.draw_level_complete_screen()

        elif self.state == GameState.GAME_OVER:
            # Dark overlay
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.screen.blit(overlay, (0, 0))

            msg = ">>> MISSION FAILED <<<"
            msg_surface = self.font.render(msg, True, (255, 100, 100))
            rect = msg_surface.get_rect(center=(self.screen_width//2, self.screen_height//2 - 20))
            self.screen.blit(msg_surface, rect)

            retry_msg = "Press R to restart level"
            retry_surface = self.small_font.render(retry_msg, True, (255, 200, 200))
            retry_rect = retry_surface.get_rect(center=(self.screen_width//2, self.screen_height//2 + 10))
            self.screen.blit(retry_surface, retry_rect)

        elif self.state == GameState.AIMING:
            msg = ">> Click and drag spaceship to aim, release to launch! <<"
            msg_surface = self.small_font.render(msg, True, (255, 255, 150))
            self.screen.blit(msg_surface, (10, self.screen_height - 30))

        elif self.state == GameState.FLYING:
            self.draw_thrust_hud()

        # Navigation controls
        progress = self.level_manager.get_level_progress()
        nav_parts = []

        if progress['can_go_previous']:
            nav_parts.append("P=Prev")
        else:
            nav_parts.append("P=Prev(locked)")

        if progress['can_go_next']:
            nav_parts.append("N=Next")
        else:
            nav_parts.append("N=Next(locked)")

        nav_text = " | ".join(nav_parts)
        controls_text = f"R=Restart | {nav_text} | M=Level Select | DRAG=Aim | ESC=Quit"

        if progress['can_go_next'] and progress['can_go_previous']:
            help_color = (180, 180, 255)
        else:
            help_color = (255, 200, 150)

        help_surface = self.small_font.render(controls_text, True, help_color)
        self.screen.blit(help_surface, (10, self.screen_height - 60))

    def draw_level_complete_screen(self):
        """v2.0: Draw animated level complete screen with stars"""
        # Dark overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        # Title
        msg = "*** LEVEL COMPLETE! ***"
        msg_surface = self.title_font.render(msg, True, (100, 255, 150))
        rect = msg_surface.get_rect(center=(self.screen_width//2, self.screen_height//2 - 70))
        self.screen.blit(msg_surface, rect)

        # v2.0: Animated star rating
        star_size = 32
        star_y = self.screen_height // 2 - 20
        star_start_x = self.screen_width // 2 - (3 * (star_size + 10)) // 2

        for i in range(3):
            star_x = star_start_x + i * (star_size + 10)
            # Animate stars appearing one by one
            delay = i * 0.4
            if self.star_display_timer > delay:
                if i < self.stars_earned:
                    # Earned star with pop animation
                    scale_progress = min(1.0, (self.star_display_timer - delay) / 0.3)
                    # Bounce effect
                    if scale_progress < 0.5:
                        scale = scale_progress * 2.6
                    else:
                        scale = 1.3 - (scale_progress - 0.5) * 0.6
                    scale = max(0, min(1.3, scale))

                    actual_size = int(star_size * scale)
                    color = (255, 215, 0)
                    self.draw_star_shape(star_x + star_size // 2, star_y, actual_size // 2, color)
                else:
                    # Unearned star
                    self.draw_star_shape(star_x + star_size // 2, star_y, star_size // 2,
                                       (80, 80, 80), filled=False)

        # Rating text
        if self.stars_earned == 3:
            rating_text = "PERFECT!"
            rating_color = (255, 215, 0)
        elif self.stars_earned == 2:
            rating_text = "Great job!"
            rating_color = (200, 200, 100)
        else:
            rating_text = "Completed!"
            rating_color = (150, 200, 150)

        if self.star_display_timer > 1.2:
            rating_surface = self.font.render(rating_text, True, rating_color)
            rating_rect = rating_surface.get_rect(center=(self.screen_width//2, self.screen_height//2 + 30))
            self.screen.blit(rating_surface, rating_rect)

        # Navigation hint
        progress = self.level_manager.get_level_progress()
        if progress['can_go_next']:
            next_msg = "Press N for next level, R to replay for more stars"
            next_color = (150, 255, 150)
        else:
            next_msg = "All levels completed! You're a master pilot! Press R to replay"
            next_color = (255, 255, 100)

        if self.star_display_timer > 1.5:
            next_surface = self.small_font.render(next_msg, True, next_color)
            next_rect = next_surface.get_rect(center=(self.screen_width//2, self.screen_height//2 + 70))
            self.screen.blit(next_surface, next_rect)

    def draw_level_select(self):
        """v2.0: Draw level selection screen"""
        # Title
        title = f"GRAVITY WELLS v{VERSION} - LEVEL SELECT"
        title_surface = self.title_font.render(title, True, (100, 200, 255))
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 50))
        self.screen.blit(title_surface, title_rect)

        # Star count
        total_stars = self.level_manager.get_total_stars()
        max_stars = self.level_manager.get_max_possible_stars()
        star_text = f"Total Stars: {total_stars}/{max_stars}"
        star_surface = self.font.render(star_text, True, (255, 215, 0))
        star_rect = star_surface.get_rect(center=(self.screen_width // 2, 95))
        self.screen.blit(star_surface, star_rect)

        # Draw level grid
        cols = 4
        cell_w = 200
        cell_h = 120
        start_x = (self.screen_width - cols * cell_w) // 2
        start_y = 140

        for i in range(len(self.level_manager.levels)):
            row = i // cols
            col = i % cols
            x = start_x + col * cell_w
            y = start_y + row * cell_h

            level = self.level_manager.levels[i]
            unlocked = self.level_manager.is_level_unlocked(i)
            completed = self.level_manager.is_level_completed(i)
            stars = self.level_manager.get_level_stars(i)
            is_current = (i == self.level_manager.current_level_index)

            # Cell background
            rect = pygame.Rect(x + 10, y + 10, cell_w - 20, cell_h - 20)

            # Check hover
            is_hovered = rect.collidepoint(self.mouse_pos.x, self.mouse_pos.y)

            if not unlocked:
                bg_color = (20, 15, 30)
                border_color = (60, 50, 70)
            elif completed:
                bg_color = (10, 40, 20)
                border_color = (50, 150, 70)
            elif is_current:
                bg_color = (15, 25, 45)
                border_color = (80, 150, 255)
            else:
                bg_color = (15, 15, 35)
                border_color = (60, 80, 120)

            if is_hovered and unlocked:
                bg_color = tuple(min(255, c + 20) for c in bg_color)
                border_color = tuple(min(255, c + 40) for c in border_color)

            pygame.draw.rect(self.screen, bg_color, rect)
            border_width = 3 if is_current else 2
            pygame.draw.rect(self.screen, border_color, rect, border_width)

            if unlocked:
                # Level number
                num_text = f"Level {i + 1}"
                num_color = (200, 200, 255) if not completed else (100, 255, 100)
                num_surface = self.small_font.render(num_text, True, num_color)
                self.screen.blit(num_surface, (x + 18, y + 18))

                # Level name (truncated)
                name = level.name[:20] + "..." if len(level.name) > 20 else level.name
                name_surface = self.small_font.render(name, True, (180, 180, 200))
                self.screen.blit(name_surface, (x + 18, y + 40))

                # Stars
                if stars > 0:
                    self.draw_stars(x + 18, y + 65, stars, 12)

                # Max shots info
                shots_text = f"Shots: {level.max_shots}"
                shots_surface = self.small_font.render(shots_text, True, (140, 140, 160))
                self.screen.blit(shots_surface, (x + 18, y + 85))
            else:
                # Locked indicator
                lock_text = "LOCKED"
                lock_surface = self.font.render(lock_text, True, (80, 60, 90))
                lock_rect = lock_surface.get_rect(center=(rect.centerx, rect.centery))
                self.screen.blit(lock_surface, lock_rect)

        # Instructions
        hint = "Click a level to play | ESC to go back"
        hint_surface = self.small_font.render(hint, True, (150, 150, 180))
        hint_rect = hint_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 30))
        self.screen.blit(hint_surface, hint_rect)

    def draw_gravity_info(self):
        """Draw information about gravity types"""
        if not self.current_level:
            return

        planets = [obj for obj in self.current_level.objects if hasattr(obj, 'color_type')]
        has_wormholes = any(isinstance(obj, Wormhole) for obj in self.current_level.objects)

        if planets or has_wormholes:
            info_y = 132
            info_text = "*** Field Types ***"
            info_surface = self.small_font.render(info_text, True, (255, 255, 150))
            self.screen.blit(info_surface, (10, info_y))
            info_y += 25

            # Show unique gravity types
            shown_types = set()
            for planet in planets:
                if planet.color_type not in shown_types:
                    gravity_strength = planet.mass / planet.base_mass
                    color = planet.color

                    if "Heavy" in planet.color_type:
                        symbol = "[R]"
                    elif "Super Heavy" in planet.color_type:
                        symbol = "[P]"
                    elif "Light" in planet.color_type:
                        symbol = "[G]"
                    elif "Variable" in planet.color_type:
                        symbol = "[Y]"
                    elif "Normal" in planet.color_type:
                        symbol = "[B]"
                    else:
                        symbol = "[*]"

                    type_text = f"  {symbol} {planet.color_type}: {gravity_strength:.1f}x"
                    enhanced_color = (min(255, color[0] + 50),
                                    min(255, color[1] + 50),
                                    min(255, color[2] + 50))
                    type_surface = self.small_font.render(type_text, True, enhanced_color)
                    self.screen.blit(type_surface, (10, info_y))
                    info_y += 20
                    shown_types.add(planet.color_type)

            # v2.0: Show wormhole info
            if has_wormholes:
                wormhole_text = "  [W] Wormhole: Teleport!"
                wormhole_surface = self.small_font.render(wormhole_text, True, (100, 220, 255))
                self.screen.blit(wormhole_surface, (10, info_y))

    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
