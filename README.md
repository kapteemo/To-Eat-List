# To-Eat-List

#### Video Demo:  <URL HERE>

## Description

This project is my final submission for CS50. Basically, it is a web application that works just like a "To-Do List," but specifically for food. Instead of writing down chores like "do the laundry," you may write down "Sushi from that new spot downtown." It helps users keep track of their cravings so they never have to face the "what should we eat?" struggle again. It also has a fun feature that picks a random food for you if you really can't decide.

I built this using Python and Flask for the back end, a SQL database to store all the information, and HTML, CSS, and JavaScript for the front end. I wanted it to look warm and appetizing, so I used a special color palette with deep greens, creams, and oranges.

## I Used

- __Python__
- __Flask__
- __SQLite__
- __HTML5 and Jinja2__
- __CSS3__
- __JavaScript__
- __Flask Sessions__

## My Project Structure
### Here is a breakdown of all the files I wrote for this project and what each one of them does.

- `app.py`  
  The main file that runs everything. All the web addresses live here. This file handles signing up, logging in, making lists, adding foods, editing things, deleting things, and picking random foods. The file also starts the website, checks if you're logged in, and makes sure you only see your own lists.

- `database.py`  
  Sets up the database where everything gets saved. Creates three storage areas: one for usernames and passwords, one for list names and who owns them, and one for food items and which list they belong to. You run this file once at the beginning to set up these storage areas with the right connections between them.

- `layout.html`  
  The base template that every page uses. Has the menu bar at the top, the header styling, and the footer. This gives every page the same look and navigation.

- `index.html`  
  The home page. Shows the big "To-Eat-List" title, the "Let's Plan" button, and the colored boxes. This page tells people what the site does with big bold text and eye-catching design.

- `auth_layout.html`  
  A special template for login and signup pages. Removes the menu bar so these pages look cleaner and more focused. Uses a centered card layout that works better for forms.

- `login.html`  
  The login form where you type your username and password. Uses auth_layout.html and includes a link to the signup page if you need to make an account.

- `register.html`  
  The signup form where you make a new account by picking a username and password. Uses auth_layout.html and includes a link back to the login page.

- `create.html`  
  A simple form where you make a new food list by typing in a name. Sends the name to the server to save your new list.

- `my_lists.html`  
  Your main page that shows all your food lists in accordion format. Each list looks like a card with the list name and edit and delete buttons on top. Click the card to open it and see all the foods inside. You edit each food by clicking on it. You delete foods by clicking the trash icon. All changes happen through background requests so the page never reloads.

- `random.html`  
  The random food page. Shows one random food at a time. You pick which list you want to add it to from a dropdown menu. One button adds the food to your chosen list. Another button gets you a new random food.

- `style.css`  
  All the visual styling. Includes the colors, fonts, spacing, and layouts. Defines how the home page looks (full screen background, big headline, button styling), how the accordion cards look (brown headers, cream backgrounds), how forms look (input boxes, submit buttons), and how everything adjusts for phones (screens under 768px wide).

- `my_lists.js`  
  Makes the accordion work and handles editing. Opens and closes list cards when you click the headers. Changes text into input boxes when you edit list names and food items. Sends background requests to save or delete items. Removes deleted items from the page right away. Stops action buttons from opening the accordion when you click them.
