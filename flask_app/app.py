from main import create_app

ENV = 'dev'
app = create_app(ENV)

if __name__ == '__main__':
    app.run()