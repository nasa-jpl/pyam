//the mysql-js object through which we connect with the db
const mysql = require('mysql')

const db = mysql.createConnection({
host: "dartslab.jpl.nasa.gov",
// user: "",
password: "dlabyam",
database:"YaMDshell" 
})

module.exports = db;

// # connection parameters for the YaM MySQL database
// $mysqlPort = "localhost.localdomain:3306";
// $mysqlPort = "dartslab.jpl.nasa.gov";
// $mysqlUser = "yam";
// $mysqlPassword = "dlabyam";
