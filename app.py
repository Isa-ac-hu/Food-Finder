from flask import Flask, render_template, url_for, request
from urllib.request import urlopen

############################################################################
class FoodType:
    name = ""
    protein = 0
    appearance_dates = []
    unique_date = ""
    meal = ""
    dining_hall = ""

    def __init__(self, name, protein, unique_date, meal, dining_hall):
        self.name = name
        self.protein = protein
        self.unique_date = unique_date
        self.meal = meal
        self.dining_hall = dining_hall

marciano = "https://www.bu.edu/dining/location/marciano/#menu"
west = "https://www.bu.edu/dining/location/west/#menu"
warren = "https://www.bu.edu/dining/location/warren/#menu"

locations = [marciano, west, warren]
list_of_foods = []

for dining_hall in locations:
    page = urlopen(dining_hall)
    html = page.read().decode("utf-8")
    protein_content = 0
    looking_at_contents = True
    content_line = ""
    current_date = ""
    current_meal = ""
    dining_hall_name = ""
    if(dining_hall == locations[0]):
        dining_hall_name = "Marciano"
    elif(dining_hall == locations[1]):
        dining_hall_name = "West"
    elif (dining_hall == locations[2]):
        dining_hall_name = "Warren Towers"

    for line in html.splitlines():
        #fix any strangely read characters
        if "&#039;" in line:
            line = line.replace("&#039;", "'")
        if "&amp;" in line:
            line = line.replace("&amp;", "&")
        if "&quot;" in line:
            line = line.replace("&quot;", "\"")

        #we're looking at a food item
        if "menu-item-title"  in line:
            #cut off extraneous pieces of the string
            line = line.split(">", 1)[1]
            line = line.split("<", 1)[0]
            line = line.replace(' ', "_")
            if looking_at_contents:
                content_line = line
                looking_at_contents = False
            else:
                current_food = FoodType(content_line, protein_content, current_date,
                                        current_meal, dining_hall_name)
                list_of_foods.append(current_food)
                looking_at_contents = True

            #reset protein content
            protein_content = 0

        #PROTEIN
        elif "menu-nutrition-protein" in line:
            #cut off extraneous pieces of the string
            line = line.split(">")[2]
            line = line.split("<")[0]
            #remove the final g
            line = line[:-1]
            try:
                line_int = int(line)
                protein_content += line_int
            except:
                protein_content = 0

        #we're looking at the date
        elif "menu-bydate-title" in line:
            #cut off extraneous pieces of the string
            line = line.split(">", 1)[1]
            line = line.split("<", 1)[0]
            current_date = line

        elif "meal-period-breakfast" in line:
            current_meal = "Breakfast"
        elif "meal-period-lunch" in line:
            current_meal = "Lunch"
        elif "meal-period-dinner" in line:
            current_meal = "Dinner"

#we sort our list, the x. part tells us what parameter to sort by
list_of_foods.sort(key=lambda x: x.name, reverse=False)

#new idea, we sort the list of foods by name, so that consecutive items will share a name,
#thus their different unique dates can be compiled into a full list of appearances

appearances = []
for i in range(0, len(list_of_foods)-1):
    if list_of_foods[i].name == list_of_foods[i+1].name:
        appearances.append(list_of_foods[i].unique_date + " for " + list_of_foods[i].meal)
    else:
        appearances.append(list_of_foods[i].unique_date)
        list_of_foods[i].appearance_dates = appearances
        appearances = []

list_of_unique_foods = []
for obj in list_of_foods:
    if obj.appearance_dates:
        list_of_unique_foods.append(obj)

#because list of foods was already sorted we dont need to sort list of unique foods
#unless we'd like to sort by something else like protein or date


def earliest_appearance(food_name):
    for food in list_of_unique_foods:
        if food.name == food_name:
            return "The food you selected will return on " + food.appearance_dates[0]
    return "This food does not appear in our projected range."




###############################################################################
app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html', list=list_of_unique_foods, food="",
                           appearance="", protein="", hall="")


@app.route('/result', methods=['POST', 'GET'])
def result():
    food = ""
    appearance = ""
    protein = ""
    hall = ""
    for i in list_of_unique_foods:
        if request.form.get('action1') == i.name:
            food = i.name.replace("_", " ")
            appearance = earliest_appearance(i.name)
            protein = str(i.protein) + " grams"
            hall = i.dining_hall

    return render_template('index.html', list = list_of_unique_foods, food = food,
                           appearance = appearance, protein = protein, hall = hall)


if __name__ == "__main__":
    app.run(debug=True, port=5001)


