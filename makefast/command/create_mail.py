import click
import os
from makefast.utils import generate_class_name, convert_to_snake_case, convert_to_hyphen

class CreateMail:
    @staticmethod
    def execute(name: str):
        class_name = generate_class_name(name)
        file_name = convert_to_snake_case(name)
        view_name = convert_to_hyphen(name)
        
        # 1. Create Mailable class
        mail_dir = "app/mail"
        if not os.path.exists(mail_dir):
            os.makedirs(mail_dir, exist_ok=True)
            with open(os.path.join(mail_dir, "__init__.py"), "w") as f:
                f.write("")
                
        mail_file_path = f"{mail_dir}/{file_name}.py"
        
        mail_template = f"""from makefast.mail import Mailable

class {class_name}(Mailable):
    def __init__(self, data: dict = None):
        super().__init__()
        self.mail_data = data or {{}}

    def build(self):
        return (
            self.view("emails.{view_name}")
                .with_data(**self.mail_data)
                .subject("Subject for {class_name}")
        )
"""
        with open(mail_file_path, "w") as f:
            f.write(mail_template)
            
        # 2. Create HTML View
        views_dir = "resources/views/emails"
        if not os.path.exists(views_dir):
            os.makedirs(views_dir, exist_ok=True)
            
        view_file_path = f"{views_dir}/{view_name}.html"
        
        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{class_name}</title>
</head>
<body>
    <h2>Hello from {class_name}!</h2>
    <p>This is a default template for your email.</p>
    
    <!-- Example of using passed data -->
    <!-- <p>Data: {{{{ key }}}}</p> -->
</body>
</html>
"""
        if not os.path.exists(view_file_path):
            with open(view_file_path, "w") as f:
                f.write(html_template)
                
        click.echo(f"Mailable [{mail_file_path}] created successfully.")
        click.echo(f"Mail view [{view_file_path}] created successfully.")
