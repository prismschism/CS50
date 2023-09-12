    # Project: Travel blog/ Image Hosting Webapp
    ### Video Demo:
    #### Description:

        My final project consists of an idea I had for a travel blog/ image hosting webapp that allows users to post images.
        The site allows users to upload images of their travels, along with a location and short description of the site they took the photo of.

        The goal of the webapp is mainly to share travel locations with others so that other people may discover new locations or "spots" to visit when
        traveling themselves. It aims to be a webapp of similar experience to that of the early days of instagram, except there is less of a social media vibe
        and more of an adventure discovery and sharing experience. It is ideally to be used as a form of expression and inspiration for travel activities.

        A new user will be greeted by a landing page that encourages the user to start using the service with the only two options of registering for a new account or loging
        in to an existing user account.

        The users are required to register to use the webapp by providing an email address and username which are stored as plaintext.
        The users must also set up a "strong" password by creating and confirming a password which is at least 8 characters long, contains letters/numbers and has capitalization. The password is then hashed and only the hash is stored in the Database so as to protect the user's password and account by not storing it
        as plain text.

        Once the user has registered, they are greeted with a home page that allows the user to stay logged in while using the site or log out when desired.
        Once the user is logged in, they see the HOME page with a navbar that has the options: 'Home', 'Post a Spot', 'Profile', and 'Log out'

        The HOME option which takes the user to the main screen where they can view their recent visited/uploaded locations/pictures.

        The navbar also has a link to Post a Spot, which is the web page where the user can upload a new photo along with its relevant information.
        The images must meet the condition of ending in extensions such as 'png', 'jpg', 'jpeg', 'gif'. They are then converted to BLOB then stored in the Database, linking the images to the specific userID of the user who uploaded the image.
