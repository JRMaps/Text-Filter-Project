# ALT-FIL-ter-Project
Github Repository for Autoamata &amp; Language Theory Project Titled "FIL-ter"

# BACKEND

## Folder Structure (Will update as the project progress)
    backend/
    ├── app/
    │   ├── main.py              # Application entry point
    │   ├── auth/                # JWT Authentication & Identity management
    │   ├── user/                # User profiles & account logic
    │   ├── conversation/        # Chat session management
    │   ├── message/             # Message persistence and history
    │   ├── websocket/           # Real-time communication & Connection Manager
    │   ├── moderation/          # The "Brain": CFG, Tokenizer, & Normalization
    │   ├── core/                # Shared dependencies & global security
    │   └── database/            # SQLAlchemy engine & session configuration
    ├── .env                     # Environment variables (Sensitive)
    ├── .gitignore
    └── requirements.txt

## Configuring Backend Dependencies

To set up the backend, follow these steps:

1. **Install Python Dependencies**:
   - Ensure you have Python installed (preferably version 3.9 or higher).
   - Create and activate a virtual environment:
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
     ```
   - Install the required dependencies:
     ```bash
     pip install -r requirements.txt
     ```

2. **Set Up Environment Variables**:
   - Create a `.env` file in the `backend/app` directory.
   - Add the following variables:
     ```
     # DATABASE ENV VARIABLES
     DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<database_name>

     # JWT ENV VARIABLES
     SECRET_KEY=your-secret-key
     ACCESS_TOKEN_EXPIRE_MINUTES=30
     ```

3. **Database Configuration**:
   - requirement: postgresql (pwede rin yatang mysql since naka SQLAlchemy ako sa mga db operations, pero baka magkaron ng conflict sa dependencies kaya mag postgre na lang din kayo para sure haha)
   - Ensure your database server is running.
   - Update the `DATABASE_URL` in the `.env` file with your database credentials.

4. **Run the Backend Server**:
   - Start the FastAPI server (from the root folder):
     ```
     uvicorn backend.app.main:app --reload
     ```

Make sure to update the `.env` file with your specific configuration details.

