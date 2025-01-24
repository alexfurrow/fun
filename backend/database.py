#postgres

import psycopg2
from psycopg2.extras import Json

# Database connection details
DB_NAME = "stack_db"
DB_USER = "your_username"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"
DB_PORT = "5432"

# Sample JSON data
page = {
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "message": ["hey fam so i had a really good day. first i got up around 930 and then i just jammed. i basically played 3 games of dota, wherein each game i did pretty well, but i think we lost 2 of the games. it's okay, that happens. it was super chill, and i probably had 2 or 3 coffees, i was out of milk though, so i put some almonds in to soak. i had gotten a really good deal on almonds, i got 5 bags (1 lb each? .5 lbs each?) for about .31 per oz, which is way lower than normal which is like .45 to .5 per oz. anyway, i had some goals so i did some goal setting, and i hit most of them. one of the goals was to work on my side project, which i feel is coming along. i had trouble staying focused on it because i was so antsy but ultimately i was able to buckle down and focus. the moon is rising over the houston downtown skyline as im watching it, it looks huge when it does that. i've probably seen it happen like 5 times since i moved here. anyway, the houston skyline has red and white lights alternating, with some being blue. i mean the led lights that outline the top of the buildings, particularly the two tallest buildings but also several others. i learned from a friend who worked in property management for jp morgan tower, or is it wells fargo tower? whatever one of the two tallest ones are, that the mayor decides what color the downtown lights should be. it's definitely red white and blue for the texans, who lost today in a close game against the chiefs. i didn't watch much of it because i was working on my side project. anyway, i got the api call to do some prompting and stuff, and i created a bunch of other files, including my first 'class'. this is somewhat of a big deal, if writing a 'hello world' program is like taking your first baby steps (or heck, learning to roll over, or something else thats very basic), then this is like learning to ride a bike. basically as you get more sophisticated and larger programs, having classes helps keep your code organized and repeatable. so for isntance, i will be calling prompts all over my app, and so having a class that defines the different categories of prompts (think: a summary prompt, a story prompt, a poem prompt, etc.), then i can call that "class" in my program without rewriting the logic each time. it's not something you are really taught as a data scientist in training. as a software engineer its esssential. i suppose it's almost embarassing that almost 2 years into my career as a data scientist this is only the first class i've written, and its outside of work. but hey  you gotta start somewhere. and it that tells you something about where chevron is with their coding sophistication (at least for me). i do feel some pressure, like oh man, this is a lot of things to learn and get right, there are so many people that are so far ahead of me, but i'm trying not to think that way. i was mostly really  excited when i got my class to work and call it within the api and summarize my notes as a poem. i had so many more ideas burst forth, and in the evening i came back , oh by the way yeah i went out to a bar with jake and elysia and some of their friends to watch the second half of the houston texans game. i say second half because we all were a little late notice (the game was about to start when i got the invite) and i decided to squeeze in a workout before i went. i did some sprinting/z5 workouts, which went really well, but it also reminded me of  how far i have to go. i have so much excitement for where this year is going. even if i get laid off, i feel so centered and so imaginative and creative, that i feel that i have an opportunity to really come into my own. i guess im finally growing up at 33. anyway, it was a really fun time, we talked about the latest shows we were watching (severance, jake was watching some star trek, i was wathcing squidgame. we both watched severance). nora was really ecxicted to see me, and she kept saying "i have feet". i feel so happy taht children llike me, i have no idea what i did but it makes me feel like im doing something right. like im still connected to my humanity the way iprobably did as a child. idk. anyway, i came back and i was coding again and i just had too many ideas, so i decided i would get more done and be faster if i was focused on just getting the most simple thing done, which was a refinement prompt that allowed me to take long strings of text like this one and turn it into something more organized and ready for further processing. even this alone is a pretty good step. like, by analogy, if i were to draw a person, this would be like drawing a circle for the head... its kinda the first step, and i can add in all the details with time. anyway, watched the lions lose as i worked. wow cant believe theyre out in the playoffs in the divisional round. super tough. but the commanders looked so good. made me really intrgued by them. anyway. this is all to say im trying the prompt now. good luck! then i need to go to bed and sleep well, my goal now is 1130 so i have ample time in the mornign but i am still able to say up late some"],
    "restated_query": 

}







try:
    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()

    # Create a table to store JSON data
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS json_data_table (
        id SERIAL PRIMARY KEY,
        data JSONB
    );
    """)
    print("Table created successfully.")

    # Insert JSON data into the table
    cursor.execute("""
    INSERT INTO json_data_table (data)
    VALUES (%s);
    """, (Json(json_data),))
    conn.commit()
    print("JSON data inserted successfully.")

    # Retrieve JSON data from the table
    cursor.execute("""
    SELECT * FROM json_data_table;
    """)
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Data: {row[1]}")

except Exception as e:
    print(f"Error: {e}")
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
    print("Connection closed.")
