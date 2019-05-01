<?php

$link = mysqli_connect("localhost", "airbnb", "airbnb", "airbnb");

if (!$link) {
    echo "Error: Unable to connect to MySQL." . PHP_EOL;
    echo "Debugging errno: " . mysqli_connect_errno() . PHP_EOL;
    echo "Debugging error: " . mysqli_connect_error() . PHP_EOL;
    exit;
}


if (!empty($_GET['user'])) {
	$user = ($_GET['user'];
} else {
	$user = 11918986;
}
	$query_contentbased = "SELECT * FROM top10_contentbased_new tc, listings_new ls WHERE tc.listing_id = ls.id and  tc.reviewer_id='$user' order by tc.similarity desc limit 10";
	print $query_contentbased;

	$result_contentbased = mysqli_query($link, $query_contentbased);


?>
