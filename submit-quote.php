<?php
declare(strict_types=1);

const CONTACT_EMAIL = "contact@spaceupconstruction.com";
const SITE_HOST = "services.spaceupconstruction.com";
const RATE_LIMIT_SECONDS = 20;

header("Cache-Control: no-store, max-age=0");
header("X-Content-Type-Options: nosniff");
header("Referrer-Policy: same-origin");

function wants_json(): bool
{
    return strpos($_SERVER["HTTP_ACCEPT"] ?? "", "application/json") !== false;
}

function respond(int $status, string $message): void
{
    http_response_code($status);
    if (wants_json()) {
        header("Content-Type: application/json; charset=UTF-8");
        echo json_encode(
            [
                "ok" => $status >= 200 && $status < 300,
                "message" => $message,
            ],
            JSON_UNESCAPED_SLASHES,
        );
        exit();
    }

    header("Content-Type: text/html; charset=UTF-8");
    $safe_message = htmlspecialchars(
        $message,
        ENT_QUOTES | ENT_SUBSTITUTE,
        "UTF-8",
    );
    $safe_home = "https://" . SITE_HOST . "/";
    echo '<!doctype html><html lang="en-US"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Space Up Construction</title></head><body><main><h1>Space Up Construction</h1><p>' .
        $safe_message .
        '</p><p><a href="' .
        $safe_home .
        '">Return to the website</a></p></main></body></html>';
    exit();
}

function posted_value(string $key, int $max_length): string
{
    if (!isset($_POST[$key]) || !is_string($_POST[$key])) {
        return "";
    }

    $value = trim($_POST[$key]);
    $value = preg_replace('/[\x00-\x1F\x7F]+/u', " ", $value) ?? "";
    return trim(substr($value, 0, $max_length));
}

function same_origin_request(): bool
{
    $origin = $_SERVER["HTTP_ORIGIN"] ?? "";
    if ($origin === "") {
        return true;
    }

    $origin_host = strtolower((string) parse_url($origin, PHP_URL_HOST));
    if ($origin_host === SITE_HOST) {
        return true;
    }

    $test_mode =
        getenv("SPACEUP_MAIL_TEST_MODE") === "1" &&
        in_array(PHP_SAPI, ["cli", "cli-server"], true);
    return $test_mode &&
        in_array($origin_host, ["127.0.0.1", "localhost"], true);
}

function rate_limit_allows_request(): bool
{
    $client = $_SERVER["REMOTE_ADDR"] ?? "unknown";
    $file =
        sys_get_temp_dir() .
        "/spaceup-quote-" .
        hash("sha256", $client) .
        ".rate";
    $handle = @fopen($file, "c+");
    if ($handle === false) {
        return true;
    }

    $allowed = true;
    if (flock($handle, LOCK_EX)) {
        $last_attempt = (int) stream_get_contents($handle);
        $now = time();
        if ($last_attempt > 0 && $now - $last_attempt < RATE_LIMIT_SECONDS) {
            $allowed = false;
        } else {
            rewind($handle);
            ftruncate($handle, 0);
            fwrite($handle, (string) $now);
            fflush($handle);
        }
        flock($handle, LOCK_UN);
    }
    fclose($handle);
    return $allowed;
}

function acquire_submission_lock(string $submission_id): array
{
    if ($submission_id === "") {
        return [null, false];
    }

    $file =
        sys_get_temp_dir() .
        "/spaceup-quote-" .
        hash("sha256", $submission_id) .
        ".sent";
    $handle = @fopen($file, "c+");
    if ($handle === false || !flock($handle, LOCK_EX)) {
        if (is_resource($handle)) {
            fclose($handle);
        }
        return [null, false];
    }

    rewind($handle);
    return [$handle, trim((string) stream_get_contents($handle)) === "sent"];
}

function release_submission_lock($handle, bool $mark_sent): void
{
    if (!is_resource($handle)) {
        return;
    }
    if ($mark_sent) {
        rewind($handle);
        ftruncate($handle, 0);
        fwrite($handle, "sent");
        fflush($handle);
    }
    flock($handle, LOCK_UN);
    fclose($handle);
}

function deliver_message(string $subject, string $body, string $reply_to): bool
{
    $test_mode =
        getenv("SPACEUP_MAIL_TEST_MODE") === "1" &&
        in_array(PHP_SAPI, ["cli", "cli-server"], true);
    if ($test_mode) {
        return true;
    }

    $headers = [
        "From: Space Up Website <" . CONTACT_EMAIL . ">",
        "Reply-To: " . $reply_to,
        "MIME-Version: 1.0",
        "Content-Type: text/plain; charset=UTF-8",
        "X-Auto-Response-Suppress: All",
    ];

    return @mail(CONTACT_EMAIL, $subject, $body, implode("\r\n", $headers));
}

if (($_SERVER["REQUEST_METHOD"] ?? "") !== "POST") {
    header("Allow: POST");
    respond(405, "Method not allowed.");
}

if (!same_origin_request()) {
    respond(403, "This request could not be accepted.");
}

if (posted_value("company_website", 200) !== "") {
    respond(200, "Thank you. Your request has been received.");
}

$service = posted_value("service", 80);
$name = posted_value("name", 120);
$phone = posted_value("phone", 40);
$email = posted_value("email", 254);
$zip = posted_value("zip", 10);
$submission_id = posted_value("submission_id", 80);

$allowed_services = [
    "Epoxy Flooring" => "Epoxy Flooring",
    "Siding Installation and Replacement" =>
        "Siding Installation and Replacement",
];

if (!isset($allowed_services[$service])) {
    respond(422, "Please choose a valid service.");
}
if ($name === "" || strlen($name) < 2) {
    respond(422, "Please enter your name.");
}
if (!preg_match('/^[0-9+().\-\s]{7,40}$/', $phone)) {
    respond(422, "Please enter a valid phone number.");
}
if (
    preg_match('/[\r\n]/', $email) ||
    filter_var($email, FILTER_VALIDATE_EMAIL) === false
) {
    respond(422, "Please enter a valid email address.");
}
if ($zip !== "" && !preg_match('/^[0-9]{5}(?:-[0-9]{4})?$/', $zip)) {
    respond(422, "Please enter a valid ZIP code.");
}
if ($service === "Siding Installation and Replacement" && $zip === "") {
    respond(422, "Please enter your ZIP code.");
}
if (
    $submission_id !== "" &&
    !preg_match('/^[a-zA-Z0-9-]{16,80}$/', $submission_id)
) {
    respond(
        422,
        "This request could not be validated. Please reload the page and try again.",
    );
}

[$submission_lock, $already_sent] = acquire_submission_lock($submission_id);
if ($already_sent) {
    release_submission_lock($submission_lock, false);
    respond(
        200,
        "Thank you. Your request was already sent to Space Up Construction.",
    );
}
if (!rate_limit_allows_request()) {
    release_submission_lock($submission_lock, false);
    respond(429, "Please wait a moment before sending another request.");
}

$subject =
    "[Space Up Website] New " . $allowed_services[$service] . " quote request";
$body = implode("\n", [
    "New quote request from the Space Up Construction website",
    "",
    "Service: " . $allowed_services[$service],
    "Name: " . $name,
    "Phone: " . $phone,
    "Email: " . $email,
    "ZIP Code: " . ($zip !== "" ? $zip : "Not provided"),
    "",
    "Submitted: " . gmdate("Y-m-d H:i:s") . " UTC",
]);

if (!deliver_message($subject, $body, $email)) {
    release_submission_lock($submission_lock, false);
    error_log("Space Up quote form: local mail delivery failed.");
    respond(
        500,
        "We could not send your request. Please call (508) 474-9407 or try again shortly.",
    );
}

release_submission_lock($submission_lock, true);
respond(200, "Thank you. Your request was sent to Space Up Construction.");
