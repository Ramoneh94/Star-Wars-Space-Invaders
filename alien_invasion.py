import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from ship import Ship
from bullet import Bullet
from alien import Alien
# from button import Button
from scoreboard import Scoreboard
from pygame import mixer


class AlienInvasion:
    # overall class to manage game assets and behavior
    def __init__(self):
        # initialize the game and create game resources.
        pygame.init()
        self.settings = Settings()
        # CODE TO MAKE THE GAME FULLSCREEN
        # self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        # self.settings.screen_width = self.screen.get_rect().width
        # self.settings.screen_height = self.screen.get_rect().height
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion - By Ramone Henry")
        # CREATE AN INSTANCE OF GAMESTATS AND SCOREBOARD
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # Make the Play button.
        # self.play_button = Button(self, "Play")

    def run_game(self):
        # start the main loop for the game.
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self._update_screen()
                # GET RID OF BULLETS THAT HAVE DISAPPEARED.

            # Watch for keyboard and mouse events.

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_keydown_events(self, event):
        """Responds to key presses"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
            bullet_sound = mixer.Sound("blaster.wav")
            bullet_sound.play()


    def _check_keyup_events(self, event):
        "Respond to key release"
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        # Create a new bullet and add it to the bullets group.
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        # UPDATE POSITIONS OF BULLETS AND GET RID OF OLD BULLETS.
        # UPDATE BULLET POSITION
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        collisions = pygame.sprite.groupcollide(self.bullets,self.aliens,True,True)
        if not self.aliens:
             # DESTROY EXISTING BULLETS AND CREATE NEW FLEET.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            # INCREASE LEVEL.
            self.stats.level += 1
            self.sb.prep_level()
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
            explosion_sound = mixer.Sound("explosion.wav")
            explosion_sound.play()

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        # make the most recently drawn screen visible
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        # DRAW THE SCORE INFORMATION
        self.sb.show_score()

        # DRAW THE PLAY BUTTON IF THE GAME IS INACTIVE.
        # if not self.stats.game_active:
        #     self.play_button.draw_button()


        #NOTHING BELOW DISPLAY. MUST BE ABOVE
        pygame.display.flip()
        # RESET THE GAME
        # if not self.stats.game_active:
        #     self.play_button.draw_button()

    def _create_fleet(self):
        # Make an alien.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        # DETERMINE THE NUMBER OF ROWS OF ALIENS THAT FIT ON THE SCREEN.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # CREATE THE FIRST ROW OF ALIENS
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        # RESPOND APPROPRIATELY IF ANY ALIENS HAVE REACHED AN EDGE.
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        # DROP THE ENTIRE FLEET AND CHANGE THE FLEET'S DIRECTION.
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_aliens(self):

        """
        Check if the fleet is at an edge,
        then update the positions of all aliens in the fleet.

        """
        self._check_fleet_edges()
        self.aliens.update()

        # LOOK FOR ALIEN-SHIP COLLISIONS.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        # LOOK FOR ALIENS HITTING THE BOTTOM OF THE SCREEN

    def _ship_hit(self):
        # RESPOND TO THE SHIP BEING HIT BY AN ALIEN
        if self.stats.ships_left > 0:
         # DECREMENT SHIPS_LEFT.
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            chewbaca_sound = mixer.Sound("chewbaca.wav")
            chewbaca_sound.play()

        # GET RID OF ANY REMAINING ALIENS AND BULLETS.
            self.aliens.empty()
            self.bullets.empty()

            # CREATE A NEW FLEET AND CENTER THE SHIP.
            self._create_fleet()
            self.ship.center_ship()

            # PAUSE
            sleep(0.5)
        else:
            self.stats.game_active = False

    def _check_aliens_bottom(self):
        # CHECK IF ANY ALIENS HAVE REACHED THE BOTTOM OF THE SCREEN.
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # TREAT THIS THE SAME AS IF THE SHIP GOT HIT.
                self._ship_hit()
                break

if __name__ == "__main__":
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()
