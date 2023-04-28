from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.properties import BooleanProperty, StringProperty
from kivy.clock import Clock
from datetime import datetime

Builder.load_file("Python_excercises.kv")

class MyCustomWidget(FloatLayout):
    show_label = BooleanProperty(False)
    label_text = StringProperty("")

    def on_button_press(self, button_text):
        if button_text == "Day 1":
            self.label_text = "Ask the user to enter a sentence and calculate the sum of the words entered"
        elif button_text == "Day 2":
            self.label_text = "Write for loop to find the longest name in a list of 10 names"
        elif button_text == "Day 3":
            self.label_text = "Count number of words in a A4 text and print the number of words"
        elif button_text == "Day 4":
            self.label_text = "Print the longest word in a A4 text"
        elif button_text == "Day 5":
            self.label_text = "Find all 4 character words in a A4 text and sort them alphabeticaly"
        elif button_text == "Day 6":
            self.label_text = "Sum up all odd numbers between 50 and 100"
        elif button_text == "Day 7":
            self.label_text = "Write the sum of all numbers from 1-100 that are divisible by 3 and 5 without remainder"
        elif button_text == "Day 8":
            self.label_text = "Read a sentence input from user and count number of vowels using for loop"
        elif button_text == "Day 9":
            self.label_text = "Create a program that asks the user for a list of 10 numbers and then prints the even numbers using a for loop"
        elif button_text == "Day 10":
            self.label_text = "Write a program that asks the user for a list of names and then prints the names in reverse order using a while loop"
        elif button_text == "Day 11":
            self.label_text = "Create a program that reads a string input from the user and checks if it's a palindrome using a for loop"
        elif button_text == "Day 12":
            self.label_text = "Write code to calculate exchange rate for CZK to EUR"
        elif button_text == "Day 13":
            self.label_text = "Write a program that calculates the area of a triangle given its base and height"
        elif button_text == "Day 14":
            self.label_text = "Write code to calculate exchange rate for CZK to EUR"
        elif button_text == "Day 15":
            self.label_text = "Create a function that takes two lists and returns a list containing their intersection (common elements)"
        elif button_text == "Day 16":
            self.label_text = "Write a program that converts a given temperature from Celsius to Fahrenheit or vice versa"
        elif button_text == "Day 17":
            self.label_text = "Create a function that takes a list of numbers and returns the sum of the squares of the numbers"
        elif button_text == "Day 18":
            self.label_text = "Create a program that reads a CSV file and prints the total number of rows and columns in the file"
        elif button_text == "Day 19":
            self.label_text =  "Write a program that asks the user for their age and calculates the year they were born in"
        elif button_text == "Day 20":
            self.label_text = "Write a program that reads a number input from the user and prints if the number is even or odd"
        elif button_text == "Day 21":
            self.label_text = "Create a program that reads a list of words from the user and prints the words sorted alphabetically"
        elif button_text == "Day 22":
            self.label_text = "Create a program that reads a list of 5 names from the user and prints them in alphabetical order"
        elif button_text == "Day 23":
            self.label_text = "Create a program that asks the user for a list of 5 names and prints the shortest name"
        elif button_text == "Day 24":
            self.label_text = "Write a program that reads a list of 10 numbers from the user and prints the numbers in descending order"
        elif button_text == "Day 25":
            self.label_text = "Find all words that start with the letter 'b' in a list of words"
        elif button_text == "Day 26":
            self.label_text = "Find all numbers that are divisible by 2 in a list of numbers"
        elif button_text == "Day 27":
            self.label_text = "Calculate number of sentences in A4 text"
        elif button_text == "Day 28":
            self.label_text = "Calculate capital letters in A4 text"
        elif button_text == "Day 29":
            self.label_text = "Find all unique words in a list of words"
        elif button_text == "Day 30":
            self.label_text = "Calculate number of special characters in list of words"

        self.show_label = True
        Clock.schedule_once(lambda dt: self.hide_label(), 10)

    def should_enable_button(self, day_number):
        current_day = datetime.now().day
        return day_number == current_day

    def hide_label(self):
        self.show_label = False

class PythonDaysApp(App):
    def build(self):
        self.title = 'Python_Excercises'
        self.icon = 'Ceda.png'
        return MyCustomWidget()

if __name__ == '__main__':
    PythonDaysApp().run()
