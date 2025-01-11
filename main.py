from flask import Flask, render_template

# Create a flask instance
app = Flask(__name__)

# Create a route decorator
@app.route("/")
def home():
    first_name = "John"
    stuff = "This is <strong>Bold</strong> Text"
    fav_pizza_menu = ["Ham", "Cheese", "Onions"]
    return render_template("index.html", stuff=stuff, fav_pizza_menu=fav_pizza_menu)

@app.route("/user/<name>")
def user(name):
    return render_template("user.html", user=name)

# Create Custom Error pages
@app.errorhandler(404)
def page_not_found(e):
    return  render_template("404.html"), 404

# Internal server error
@app.errorhandler(500)
def page_not_found(e):
    return  render_template("500.html"), 500

if __name__ == "__main__":
    app.run(debug=True)


