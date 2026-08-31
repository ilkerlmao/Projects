import random

computer_choice = random.randint(1, 10)
guess = 0

while guess != computer_choice:
    guess = int(input("Pick a number between 1-10: "))
    if guess != computer_choice:
        print("Wrong! Try again!")

print("Correct! Good Job!")
