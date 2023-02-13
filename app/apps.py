from django.apps import AppConfig


class AppConfig(AppConfig):
    # default_auto_field = "django.db.models.BigAutoField"
    default_auto_field = "django.db.models.AutoField"
    name = "app" 
<<<<<<< HEAD
    # def ready(self):
    #     from .cron import main
    #     main()
=======
    def ready(self):
        from .cron import main
        main()
>>>>>>> fe82a2825e45d8b14d87f41bc5345a105dc09e55
