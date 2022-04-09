const bodyParser = require('body-parser');
const express = require('express');
const sessions = require('express-session');
const http = require('http');

var app = express();
const binding_ip = process.env.IP || '127.0.0.1';
var port = process.env.PORT || 1337;

var booking_host = process.env.BOOKING_HOST || '127.0.0.1';
var booking_port = process.env.BOOKING_PORT || 8070;
var profile_host = process.env.PROFILE_HOST || '127.0.0.1';
var profile_port = process.env.PROFILE_PORT || 8090;
var inventory_host = process.env.INVENTORY_HOST || "ab49a51330b3e4e14bf66798f44de061-2083756137.us-east-1.elb.amazonaws.com";
var inventory_port = process.env.INVENTORY_PORT || 8030;

//session middleware
app.use(sessions({
	name: "session_id",
	secret: "thesecretkey",
	resave: true,
	saveUninitialized: true
}));

app.use(function(req, res, next) {
  res.locals.username = req.session.username;
  next();
});

// parsing the incoming data
app.use(bodyParser.urlencoded({extended : true}));
app.use(bodyParser.json());

// cookie parser middleware
//app.use(cookieParser());

// set view engine
app.set('view engine', 'ejs');

// To use images from icons dir
app.use(express.static("public"));
app.use('/bootstrap_js', express.static(__dirname + '/node_modules/bootstrap/dist/js'));
app.use('/bootstrap_css', express.static(__dirname + '/node_modules/bootstrap/dist/css'));
app.use('/icons', express.static(__dirname + '/node_modules/bootstrap-icons/icons'));
app.use('/jquery', express.static(__dirname + '/node_modules/jquery/dist'));

// GET method of '/' access
app.get('/', function(req, res) {
	res.render('flight_search');
  /*
	  res.render('index', {
      isAuthenticated: req.session.loggedin,
      user: req.session.username
    });
		*/
});

app.get('/flight_search', function(req, res) {
	res.render('flight_search');
});

app.get('/getAllFlights/:airline', function(req, res) {
	res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify({"test": "ok", "num": 1}));
});

app.get('/flight_search/:airline', function(req, res) {
	const options = {
	  hostname: inventory_host,
	  port: inventory_port,
	  path: encodeURI('/flights/' + req.params.airline),
	  method: 'GET',
		json:true,
	  headers: {
	    'Content-Type': 'application/json',
	  }
	};

	http_req = http.request(options, get_res => {
		let rawData = '';
		get_res.on('data', (chunk) => { rawData = chunk; });
		get_res.on('end', () => {
	    try {
				// Return JSON reply to the caller
			  res.json(JSON.parse(rawData));
	    } catch (e) {
	      console.error(e.message);
	    }
	  });
	})
	http_req.on('error', error => {
	  console.error(error)
	})

	//http_req.write(data)
	http_req.end()
});

app.get('/booking_history', function(request, res) {
	if(!request.session.username) {
		res.redirect('/login')
		return;
	}
	const data = JSON.stringify({
	  username: request.session.username,
		password: request.session.password
	})

	const options = {
		hostname: profile_host,
		port: profile_port,
		path: encodeURI('/allBookings'),
		method: 'POST',
		json: true,
		headers: {
		  'Content-Type': 'application/json',
			'Content-Length': data.length
		}
	}
	http_req = http.request(options, http_res => {
		let rawData = '';
		http_res.on('data', (chunk) => { rawData = chunk; });
		http_res.on('end', () => {
	    try {
				// Return JSON reply to the caller
				all_bookings = JSON.parse(rawData)["Msg"][0]["bookings"]
				console.log("Total tickets: " + all_bookings.length)
				res.render('booking_history', {data: all_bookings})
	    } catch (e) {
	      console.error(e.message);
	    }
	  });
		if(http_res.statusCode != 200) {
			console.log("All booking: Failed")
		}
	})
	http_req.on('error', error => {
	  console.error(error)
	})

	http_req.write(data)
	http_req.end()
});

app.get('/booking_history/:booking_id', function(request, res) {
	if(!request.session.username) {
		res.redirect('/login');
		return;
	}

	const data = JSON.stringify({
	  username: request.session.username,
		password: request.session.password,
		id: request.params.booking_id
	})

	const options = {
		hostname: profile_host,
		port: profile_port,
		path: encodeURI('/getBooking'),
		method: 'POST',
		json: true,
		headers: {
		  'Content-Type': 'application/json',
			'Content-Length': data.length
		}
	}
	http_req = http.request(options, http_res => {
		let rawData = '';
		http_res.on('data', (chunk) => { rawData = chunk; });
		http_res.on('end', () => {
	    try {
				// Return JSON reply to the caller
				res.render('booking_history', {detail: 'single', data: JSON.parse(rawData)["Msg"]})
	    } catch (e) {
	      console.error(e.message);
	    }
	  });
		if(http_res.statusCode != 200) {
			console.log("Get booking_id: Failed")
		}
	})
	http_req.on('error', error => {
	  console.error(error)
	})

	http_req.write(data)
	http_req.end()
});

app.get('/book_flight/:flight_id', function(req, res) {
	if(!req.session.username) {
		res.redirect('/login')
		return
	}
	res.render("book_flight", {flight_id: req.params.flight_id});
});

app.post('/book_flight/:flight_id/confirm_booking', function(req, res) {
	if(!req.session.username) {
		res.redirect('/login')
		return
	}

	const data = JSON.stringify({
		username: req.session.username,
		password: req.session.password,
		flightId: req.params.flight_id,
		flightSeats: req.body.seats,
		bookingClass: req.body.booking_class,
		bankAccount: req.body.wallet_id
	})

	const options = {
	  hostname: profile_host,
	  port: profile_port,
	  path: '/confirmBooking',
	  method: 'POST',
	  headers: {
	    'Content-Type': 'application/json',
			'Content-Length': data.length
	  }
	}

	http_req = http.request(options, response => {
		let rawData = '';
		response.on('data', (chunk) => { rawData = chunk; });
		response.on('end', () => {
	    try {
				res.render('book_flight', {booking_ok: JSON.parse(rawData)['Msg']})
	    } catch (e) {
	      console.error(e.message);
	    }
		});
		if(response.statusCode != 200) {
			console.log("Confirm Booking failed")
		}
	});
	http_req.on('error', error => {
		console.error(error)
	});

	http_req.write(data)
	http_req.end()
});

app.get('/cancel_booking/:booking_id', function(request, res) {
	if(!request.session.username) {
		res.redirect('/login')
		return;
	}

	const data = JSON.stringify({
	  username: request.session.username,
		password: request.session.password,
		id: request.params.booking_id
	})

	const options = {
		hostname: profile_host,
		port: profile_port,
		path: encodeURI('/cancelBooking'),
		method: 'POST',
		json: true,
		headers: {
		  'Content-Type': 'application/json',
			'Content-Length': data.length
		}
	}
	http_req = http.request(options, http_res => {
		let rawData = '';
		http_res.on('data', (chunk) => { rawData = chunk; });
		http_res.on('end', () => {
	    try {
				// Return JSON reply to the caller
				res.redirect('/booking_history/'+request.params.booking_id);
	    } catch (e) {
	      console.error(e.message);
	    }
	  });
		if(http_res.statusCode != 200) {
			console.log("Get booking_id: Failed")
		}
	})
	http_req.on('error', error => {
	  console.error(error)
	})

	http_req.write(data)
	http_req.end()
});

app.get('/login', function(req, res) {
	  login_type = req.query.type;
		if(login_type == undefined) {
			login_type = "login";
		}
    res.render('login', {type:login_type});
});

app.post('/auth', function(request, response) {
	if(!request.session.username || !request.session.password) {
		const data = JSON.stringify({
		  username: request.body.username,
			password: request.body.password,
		})

		const options = {
		  hostname: profile_host,
		  port: profile_port,
		  path: '/user_auth',
		  method: 'POST',
		  headers: {
		    'Content-Type': 'application/json',
				'Content-Length': data.length
		  }
		};

		http_req = http.request(options, res => {
			console.log(`User ${request.body.username} login - ${res.statusCode}`)
			if(res.statusCode == 200) {
				request.session.username = request.body.username;
				request.session.password = request.body.password;
				response.redirect('/');
			}
			else {
				response.redirect('/login?type=login_failed');
			}
		})
		http_req.on('error', error => {
		  console.error(error)
		})

		http_req.write(data)
		http_req.end()
	}
});

app.get('/logout', function(req, res) {
	req.username = null;
	req.password = null;
  req.session.destroy();
  res.redirect('/login');
});

app.get('/signup', function(req, res) {
	res.render('signup')
});

app.post('/register_user', function(request, response) {
		const data = JSON.stringify({
		  username: request.body.username,
			password: request.body.password,
			firstname: request.body.firstname,
			lastname: request.body.lastname
		})

		const options = {
		  hostname: profile_host,
		  port: profile_port,
		  path: '/createUser',
		  method: 'POST',
		  headers: {
		    'Content-Type': 'application/json',
				'Content-Length': data.length
		  }
		};

		http_req = http.request(options, res => {
			if(res.statusCode == 200) {
				response.redirect('/login?type=signup_success');
			}
			else {
				console.log(`Register user ${request.body.username} failed`)
				response.redirect('/signup?type=signup_failed');
			}
		})
		http_req.on('error', error => {
		  console.error(error)
		})

		http_req.write(data)
		http_req.end()
});

// Start the APP on the desired ip / port
app.listen(port, function() {
    console.log('http://' + binding_ip + ':' + port + '/');
});
