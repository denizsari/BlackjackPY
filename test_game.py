import pygame
from classes.player import Player
from classes.deck import Deck
from classes.croupier import Croupier
from classes.button import Button
from classes.chips import ChipDisplay


def main():
    pygame.init()

    # Define colors and set up the screen
    GREEN = (0, 128, 0)
    size = (1360, 768)
    screen = pygame.display.set_mode(size)

    # Loading various images for buttons, chips, and cards
    start_img = load_image("images/start-2.png")
    exit_img = load_image("images/exit-2.png")
    chip_images = [
        load_image("images/chipOrange.png"),
        load_image("images/chipPurple.png"),
        load_image("images/chipRed.png"),
        load_image("images/chipBlack.png"),
    ]
    deal_img = load_image("images/deal.png")
    hit_img = load_image("images/hit.png")
    stand_img = load_image("images/stand.png")
    background_card = load_image("images/BackgroundRed.png")

    center_x = size[0] // 2
    center_y = size[1] // 2

    # Setting game buttons
    start_button = Button(center_x, center_y, start_img, 1.5)
    exit_button = Button(center_x, center_y + start_img.get_height() * 2, exit_img, 1.5)
    deal_button = Button(center_x / 1.5, center_y, deal_img, 1)
    hit_button = Button(150, 400, hit_img, 1)
    stand_button = Button(250, 400, stand_img, 1)

    buttons = [start_button, exit_button]
    chip_values = [100, 200, 300, 1000]
    chip_display = ChipDisplay(chip_images)
    custom_font = pygame.font.Font("images/Pragmatica-ExtraLight.ttf", 36)

    # Initialize player, croupier, and deck
    start_game = False
    player = Player()
    croupier = Croupier()
    deck = Deck()

    x_position = 100
    y_position = 400

    # Setting initial game state
    deal_button_pressed = False
    show_buttons = False
    run = True
    player_has_stood = False
    player_busted = False
    round_ended = False
    game_over = False
    restart_game = False

    # Gizli kazanma bayrağı
    force_croupier_win = False

    #Game loop
    while run:
        screen.fill(GREEN) # Clear the screen

        for event in pygame.event.get(): # Event handling loop
            if event.type == pygame.QUIT:
                run = False # If the user quits, exit the loop
            elif event.type == pygame.MOUSEBUTTONDOWN: # Handling mouse click
                if event.button == 1: # Left mouse button clicked
                    x, y = event.pos
                    # Check if a chip is clicked and handle betting logic
                    is_over_chip, chip_index = chip_display.is_mouse_over_chip(screen, x, y)
                    if is_over_chip and not deal_button_pressed:
                        bet_amount = chip_values[chip_index]
                        player.bet(bet_amount)
                    if round_ended:  # Reset game for a new round if the previous round ended
                        player, croupier, chip_display, player_has_stood, player_busted, deal_button_pressed = reset_hands(player, croupier, chip_display, player_has_stood, player_busted, deal_button_pressed)
                        round_ended = False
                        if player.balance == 0:
                            game_over = True
                    if restart_game: # Restart game if the player balance = 0
                        deck, player, croupier = restart_game_logic(deck, player, croupier, chip_display)
                        game_over = False
                        restart_game = False
            elif event.type == pygame.KEYDOWN:
                # Gizli tuş: 'H' tuşuna basıldığında kurpiyerin kazanmasını zorla
                if event.key == pygame.K_h:
                    force_croupier_win = True
                        
        if game_over:
                chip_display.hide()
                display_text(screen, custom_font, f"Battık!", (255, 255, 255), center_x, center_y)
                display_text(screen, custom_font, f"Tekrar başlamak için tıkla!", (255, 255, 255), center_x, 450)
                restart_game = True
                
                

        # Button interaction and game flow    
        for b in buttons:
            if b.draw(screen):
                if b == start_button:
                    buttons.remove(start_button)
                    buttons.remove(exit_button)
                    start_game = True
                elif b == exit_button:
                    run = False
        
        if start_game: # Game has started
            chip_display.draw_chips(screen)
            display_text(screen, custom_font, f"Bakiye: {player.balance}M", (255, 255, 255), 1100, 700)
            display_text(screen, custom_font, f"Bet: {player.total_bet}M", (255, 255, 255), 80, 40)
            
            if player.total_bet >= 1 and not deal_button_pressed:
                if deal_button.draw(screen):
                    player.get_hand(2, deck)
                    deal_button_pressed = True
                    chip_display.hide()
                    croupier.get_hand(2, deck)

        # Display the croupier's and player's cards and handle game actions
        x_position_croupier = 500
        
        for card in croupier.hand:
            card_image = card.get_image_path()
            card_surface = pygame.image.load(card_image)
            screen.blit(card_surface, (x_position_croupier, 50))
            x_position_croupier += 95

        x_position = 500
        y_position = 500

        for card in player.hand:
            card_image = card.get_image_path()
            card_surface = pygame.image.load(card_image)
            screen.blit(card_surface, (x_position, y_position))
            x_position += 95
            player_hand_value = deck.calculate_hand_value(player.hand)
            display_text(screen, custom_font, f"{player_hand_value}", (255, 255, 255), 600, 450)

            if not player_has_stood and not player_busted:
                screen.blit(background_card, (600, 50))
                first_card = croupier.hand[0]
                croupier_hand_value = deck.calculate_hand_value([first_card])
                display_text(screen, custom_font, f"{croupier_hand_value}", (255, 255, 255), 600, 290)
                if hit_button.draw(screen):
                    player.get_hand(1, deck)
                    if deck.calculate_hand_value(player.hand) >= 22:
                        player_busted = True

                if stand_button.draw(screen):
                    player_has_stood = True
                    croupier.logic(deck)
                    
        start_again_text = custom_font.render("Tekrar başlamak için tıkla!", True, (255, 255, 255))
        # Display results if the player busts or stands
        if player_busted:
            croupier_hand_value = deck.calculate_hand_value(croupier.hand)
            display_text(screen, custom_font, f"{croupier_hand_value}", (255, 255, 255), 600, 290)
            user_new_balance = player.balance
            pygame.draw.rect(screen, GREEN, (565, 600, 30, 30))
            display_text(screen, custom_font, f"Oyuncu kaybetti!", (255, 255, 255), center_x, center_y)
            display_text(screen, custom_font, f"Tekrar başlamak için tıkla!", (255, 255, 255), center_x, 450)
            round_ended = True
            
        if player_has_stood or player_busted:
            # Kurpiyerin kazanmasını sağla, eğer bayrak aktifse
            if force_croupier_win:
                player_hand_value = 0  # Oyuncunun elini sıfırla
                croupier_hand_value = 21  # Kurpiyerin eli kazansın
                force_croupier_win = False  # Bayrağı sıfırla, sonraki elde normal oynasın

            #Player stands
            croupier.logic(deck) # Croupier stands with 17
            croupier_hand_value = deck.calculate_hand_value(croupier.hand) 
            display_text(screen, custom_font, f"{croupier_hand_value}", (255, 255, 255), 600, 290)

            if deck.calculate_hand_value(player.hand) == 21 and len(player.hand) == 2:
                display_text(screen, custom_font, f"Blackjack! Oyuncu kazandı!", (255, 255, 255), center_x, center_y)
                player.balance += player.total_bet * 2.5
                round_ended = True

            elif croupier_hand_value == 21 and len(croupier.hand) == 2:
                display_text(screen, custom_font, f"Blackjack! Kurpiyer kazandı!", (255, 255, 255), center_x, center_y)
                round_ended = True

            elif croupier_hand_value > 21:
                display_text(screen, custom_font, f"Kurpiyer battı! Oyuncu kazandı!", (255, 255, 255), center_x, center_y)
                player.balance += player.total_bet * 2
                round_ended = True

            elif player_hand_value > croupier_hand_value:
                display_text(screen, custom_font, f"Oyuncu kazandı!", (255, 255, 255), center_x, center_y)
                player.balance += player.total_bet * 2
                round_ended = True

            elif player_hand_value < croupier_hand_value:
                display_text(screen, custom_font, f"Kurpiyer kazandı!", (255, 255, 255), center_x, center_y)
                round_ended = True

            else:
                display_text(screen, custom_font, f"Berabere!", (255, 255, 255), center_x, center_y)
                player.balance += player.total_bet
                round_ended = True

            # Eğer oyun sona erdiyse yeniden başlatma işlemleri
            if round_ended and player.balance == 0:
                game_over = True

        pygame.display.update()  # Update the display

    pygame.quit()  # Quit the game


def load_image(path):
    return pygame.image.load(path)


def display_text(screen, font, text, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)


def reset_hands(player, croupier, chip_display, player_has_stood, player_busted, deal_button_pressed):
    player.reset_hand()
    croupier.reset_hand()
    chip_display.reset_bet()
    player_has_stood = False
    player_busted = False
    deal_button_pressed = False
    return player, croupier, chip_display, player_has_stood, player_busted, deal_button_pressed


def restart_game_logic(deck, player, croupier, chip_display):
    deck = Deck()
    player = Player()
    croupier = Croupier()
    chip_display = ChipDisplay(chip_images)
    return deck, player, croupier


if __name__ == "__main__":
    main()
