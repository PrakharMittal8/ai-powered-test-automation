package com.automation.utils;
import java.io.FileInputStream;
import java.util.Properties;

public class ConfigReader {

    private static Properties prop;

    static {
        try {

            String env = System.getProperty("env", "qa");
            
            FileInputStream fis = new FileInputStream(
                    "src/test/resources/config-" + env + ".properties"
            );

            prop = new Properties();
            prop.load(fis);

        } catch (Exception e) {
            throw new RuntimeException("Failed to load config file");
        }
    }

    public static String get(String key) {
        return prop.getProperty(key);
    }
}