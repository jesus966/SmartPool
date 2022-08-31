from src import api
from src import app
from src.api.resources.routes import initialize_routes

initialize_routes(api)

# Execute server if it is the main function
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9753)
