package com.automation.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;

public class LoginPage extends BasePage {

    public LoginPage(WebDriver driver) {
        super(driver);
    }

    private By email = By.id("userEmail");
    private By password = By.id("userPassword");
    private By loginBtn = By.id("login");

    public void login(String user, String pass) {
        type(email, user);
        type(password, pass);
        click(loginBtn);
    }
}