import random

def game():
    print('Welcome to my game!')
    while True:
        print('\n1. Start Game')
        print('2. View Rules')
        print('3. Quit Game')
        choice = input('Choose an option: ')
        if choice == '1':
            start_game()
        elif choice == '2':
            view_rules()
        elif choice == '3':
            print('Thanks for playing!')
            sys.exit()
        else:
            print('Invalid choice. Please choose a valid option.')
if __name__ == '__main__':
    game()