# Airticket Price Tracker
Get email notifications when there is a change in AirAsia Ticket Prices.

## What is this
This python script monitors the [Air Asia Booking Page](http://www.airasia.com/in/en/home.page?cid=1) for any changes. An email is sent to the user whenever there is a change.

## Why
To save the F5 key from incessant torture.


## How To
1. Clone this repository.
    ```
    $ git clone https://github.com/sharad5/airticket-price-tracker.git
    ```

2. Install the requirements.
    ```
    $ pip install -r requirements.txt
    ```

3. Enter sender's email (gmail), password and receiver's email(s) (any) in ```airticket-price-tracker.py```.
    ```
    from_addr = "SENDER_EMAIL"
    to_addr = ["RECEIVER_EMAIL", "RECEIVER_EMAIL"]
    ...
    server.login(from_addr, "PASSWORD")
    ```
    You can even enter the same email (gmail) in sender and receiver to send emails to yourself.

4. Run the script.
    Only runs on Python 3.x
    ```
    $ python airticket-price-tracker.py 600
    ```
    ```600``` is the time interval (in seconds) after which the script will check if the airfare page has changed. This wait-check process will go on, unless stopped using ```Ctrl-C```.

5. Run this script on your machine or on a server.

    ![Email from AirTicket Price tracker](http://i.imgur.com/g6Mz0qQ.jpg "Email from AirTicket Price tracker")

6. Enjoy.

##License
[MIT](https://github.com/sharad5/airticket-price-tracker/blob/master/LICENSE)
