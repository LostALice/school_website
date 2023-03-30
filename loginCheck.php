<!DOCTYPE php>
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
		$num1 = $_POST["num1"];
		$num2 = $_POST["num2"];
		$operator = $_POST["operator"];

		switch ($operator) {
			case "add":
				$result = $num1 + $num2;
				break;
			case "subtract":
				$result = $num1 - $num2;
				break;
			case "multiply":
				$result = $num1 * $num2;
				break;
			case "divide":
				if ($num2 == 0) {
					$result = "Error: division by zero";
				} else {
					$result = $num1 / $num2;
				}
				break;
			default:
				$result = "Error: invalid operator";
				break;
		}

		echo "<br><br><strong>Result:</strong> " . $result;
	}
	?>

    <h2><?php echo $sum; ?></h2>
</body>
</html>