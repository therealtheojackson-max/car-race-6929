import os
import sys

# Run a headless smoke-check for the Pygame game.
# It sets SDL_VIDEODRIVER to 'dummy' so the display can be initialized
# in headless environments, imports classes from main, and simulates
# a few frames of updates + drawing to ensure there are no runtime errors.

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import pygame

try:
    # Import constants and classes from the main game
    from main import (WIDTH, HEIGHT, PlayerCar, NPCCar, Island, Building, Garage, 
                      DecorationShop, Home, Race, ISLANDS, IS_MOBILE, CAR_MODELS, 
                      RACE_DIFFICULTIES, DECORATIONS, HOUSE_TIERS, draw_world)
except Exception as e:
    print("ERROR: failed to import from main.py:", e)
    raise


def run_smoke(frames=15):
    pygame.init()
    # Use a small, headless display surface
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # Initialize islands at module level
    import main
    main.ISLANDS_OBJ = [Island(island_data) for island_data in ISLANDS]

    # Create player on first island
    island_data = ISLANDS[0]
    player = PlayerCar(island_data['x'] + island_data['width'] // 2, island_data['y'] + island_data['height'] // 2)
    player.current_island = 0
    player.currency = 500  # Starting money
    
    # Create NPCs on the island
    npc1 = NPCCar(island_data['x'] + 50, island_data['y'] - 80, 3.5, 0)
    npc2 = NPCCar(island_data['x'] + 100, island_data['y'] - 200, 2.8, 0)
    npcs = [npc1, npc2]

    # Create a mock keys object (all keys unpressed initially)
    keys = pygame.key.get_pressed()
    
    # Test info
    print(f"Device detection: IS_MOBILE={IS_MOBILE}")
    print(f"Screen size: {WIDTH}x{HEIGHT}")
    print(f"Race difficulties: {len(RACE_DIFFICULTIES)} levels")
    print(f"Decorations available: {len(DECORATIONS)}")
    print(f"House upgrade tiers: {len(HOUSE_TIERS)}")
    print(f"Starting player money: ${player.currency}")
    print(f"Starting house: {player.home.get_current_tier()['name']}")

    # Simulate a race
    active_race = None
    races_won = 0
    
    for f in range(frames):
        # Simulate earning money
        if f == 2:
            player.currency += 100
            print(f"  [frame {f}] Player earned $100")
        
        # Simulate buying decoration at frame 3
        if f == 3:
            if player.buy_decoration(DECORATIONS[0]):
                print(f"  [frame {f}] Bought decoration: {DECORATIONS[0]['name']}")
        
        # Simulate starting a race at frame 5
        if f == 5 and not active_race:
            active_race = Race(npc1, races_won)
            print(f"  [frame {f}] RACE STARTED - Difficulty: {active_race.difficulty['name']}, Prize: ${active_race.prize_money}")
        
        # Simulate house upgrade at frame 8
        if f == 8:
            player.currency += 1500  # Give enough for upgrade
            if player.buy_house_upgrade():
                print(f"  [frame {f}] House upgraded to: {player.home.get_current_tier()['name']}")
        
        # Simulate race progress (player winning)
        if active_race:
            player.speed = 6  # Give player a boost for this test
            active_race.update(player.rect, player.speed)
            if active_race.finished:
                if active_race.won:
                    player.currency += active_race.prize_money
                    races_won += 1
                    print(f"  [frame {f}] RACE WON! Earned ${active_race.prize_money}")
                else:
                    print(f"  [frame {f}] RACE LOST!")
                active_race.npc.set_race_mode(False)
                active_race = None
        else:
            player.speed = 0  # Normal mode
        
        # update player and NPCs
        player.update(keys, buttons=None)
        player.move()
        for npc in npcs:
            npc.update()

        # draw to surface
        try:
            draw_world(screen)
            for npc in npcs:
                if npc.island_id == player.current_island:
                    npc.draw(screen)
            player.draw(screen)
            # flip won't error in dummy video driver
            pygame.display.flip()
        except Exception as e:
            print(f"ERROR during draw frame {f}:", e)
            raise

        # basic collision checks (should not raise)
        for npc in npcs:
            if npc.island_id == player.current_island:
                _ = player.rect.colliderect(npc.rect)

        # print a small status for realism
        race_info = ""
        if active_race:
            p_pct, n_pct = active_race.get_display_progress()
            race_info = f" | RACING: Player {p_pct}%, NPC {n_pct}%"
        print(f"frame={f} player_pos=({player.rect.x},{player.rect.y}) money=${player.currency} races_won={races_won} decorations={len(player.decoration_inventory)} house={player.home.get_current_tier()['name']}{race_info}")

    pygame.quit()
    print("SMOKE-CHECK: OK")


if __name__ == '__main__':
    try:
        run_smoke()
    except Exception as e:
        print("SMOKE-CHECK: FAILED")
        import traceback
        traceback.print_exc()
        sys.exit(2)
    sys.exit(0)
