# CS50 - Final Project - ONLINE NOTES

## *Our team*
[Pavlo Zinchenko](https://github.com/PaulSNDX)
[Daria Katsai](https://github.com/DarunkaKa)

## *RUN PROJECT*
1) Download the project;
2) Open a project in IDE (for instance, CS50 IDE);
3) Move to the project directory in the terminal (cd command);
4) Type and run the command "flask run";
5) If you do not have installed, try pip install "name" and repeat the previous step;

## *Description*
First of all, you have to register. Provide a unique username and a password.
After that, you can use your online notebook and a calendar.
To save new notes, you should write any content and press the save button.
All notes can be edited, downloaded, sorted by different algorithms or deleted.
Also, you may use the calendar tracking day function to check how many days are left.

An error message will appear when you provide incorrect input for registration, login or calendar. Follow the instructions in these messages and try again.

Examples of error messages and actions:
Must provide username - username field is empty;
Must provide password - password field is empty;
This name is already taken by another user - input another name because this one exists in the database;
Password length should be more than 7 symbols and less than 25 - incorrect password length;
Passwords don't match - confirmation password do not the same;
Incorrect credentials - maybe the user is not existing or the username/password is wrong;
There is no data. Nothing to save - you have to input data before press save.



### *Available sortes*
By alphabet order
By reversed alphabet order
By creation time

## *Calendar functional*
To add a new date - provide the event name, month, and day and press add
It will count how many days are left.
For instance, if today is 01.11.2023 and the target date (is 10.11.2023) - 9 days are left.

If it is today - you will see the following message: It`s today!
After that, you ought to delete an event. Otherwise, it will start counting again from 364 / 365 days left.

## *YouTube demonstration video*
https://youtu.be/_ND1KgHJcxE

## *FQL*
### *Can anyone make a to-do list?*
Of course, it is possible. However, you have to authorize it to your account.

### *Is there a login page?*
Certainly, your nickname and password.

### *Should I go to a login page after registration?*
No, there is implemented automatic login after registration. In other words, redirect to the dashboard.

### *Do you use a cookie to keep us logged in?*
Yes, we keep your sessions on the server, but you can log out.

### *How to open the calendar page?*
There is a hamburger menu in the top-right corner.

### *Can I restore deleted note?*
Unfortunately, it is impossible.

### *Can I create an empty note?*
You have to provide at least any symbol.

### *Is it possible to add different events with the same date?*
Sure)
