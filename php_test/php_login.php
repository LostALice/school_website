<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <?php
        if ($_SERVER["REQUEST_METHOD"] == "POST") {
            $email = $_POST["exampleInputEmail1"];
            $pw = $_POST["exampleInputPassword1"];



            echo "<br><br><strong>email:</strong> " . $email;
            echo "<br><br><strong>pw:</strong> " . $pw;
        }
	?>
</body>
</html>