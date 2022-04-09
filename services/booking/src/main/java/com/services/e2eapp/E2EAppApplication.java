package com.services.e2eapp;

import com.j256.ormlite.logger.Logger;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class E2EAppApplication {
	private static  Logger logger=null ;
	public static void main(String[] args) {
		SpringApplication.run(E2EAppApplication.class, args);
	}

}
