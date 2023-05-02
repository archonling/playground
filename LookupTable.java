

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintWriter;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashMap;
import java.util.Map;
import java.util.Timer;
import java.util.TimerTask;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

public class LookupTable {
    private static final String LOOKUP_TABLE_URL = "https://example.com/lookup_table.json";
    private static final String CACHE_FILENAME = "lookup_table_%d.json".formatted(ProcessHandle.current().pid());
    private static final String CACHE_PATH = new File(System.getProperty("java.io.tmpdir"), CACHE_FILENAME).getPath();
    private static final int DEFAULT_CACHE_REFRESH_INTERVAL = 900; // 15 minutes
    private static JSONArray lookupTable = null;

    public static void main(String[] args) {
        loadLookupTable();
        Timer timer = new Timer();
        timer.schedule(new TimerTask() {
            @Override
            public void run() {
                refreshCache();
            }
        }, 0, DEFAULT_CACHE_REFRESH_INTERVAL * 1000L);
    }

    private static JSONArray loadJsonFromUrl(String url) {
        try (InputStream is = new URL(url).openStream()) {
            return new JSONArray(new JSONTokener(is));
        } catch (IOException e) {
            System.err.printf("Unable to load JSON from URL: %s%n", url);
            return null;
        }
    }

    private static JSONArray loadJsonFromCache() {
        try (BufferedReader reader = new BufferedReader(new FileReader(CACHE_PATH))) {
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                sb.append(line);
            }
            return new JSONArray(sb.toString());
        } catch (IOException e) {
            System.err.printf("Unable to load JSON from cache file: %s%n", CACHE_PATH);
            return null;
        }
    }

    private static void saveJsonToCache(JSONArray json) {
        try (PrintWriter writer = new PrintWriter(new FileWriter(CACHE_PATH))) {
            writer.print(json.toString());
        } catch (IOException e) {
            System.err.printf("Unable to save JSON to cache file: %s%n", CACHE_PATH);
        }
    }

    private static String computeDataHash(JSONArray data) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] hash = md.digest(data.toString().getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : hash) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (NoSuchAlgorithmException e) {
            return null;
        }
    }

    private static void loadLookupTable() {
        JSONArray urlData = loadJsonFromUrl(LOOKUP_TABLE_URL);
        if (urlData == null) {
            lookupTable = null;
            return;
        }
        JSONArray cacheData = loadJsonFromCache();
        String urlHash = computeDataHash(urlData);
        if (urlHash == null) {
            lookupTable = null;
            return;
        }
        if (cacheData == null || !urlHash.equals(computeDataHash(cacheData))) {
            lookupTable = urlData;
            saveJsonToCache(lookupTable);
            System.out.println("Cache updated from URL.");
        } else {
            lookupTable = cacheData;
            System.out.println("Cache loaded from disk.");
        }
        System.out.println("Lookup table loaded.");
    }

private static void refreshCache() {
    JSONArray urlData = loadJsonFromUrl(LOOKUP_TABLE_URL);
    if (urlData == null) {
        System.err.println("Unable to refresh cache from URL.");
        return;
    }
    JSONArray cacheData = loadJsonFromCache();
    String urlHash = computeDataHash(urlData);
    if (urlHash == null) {
        System.err.println("Unable to compute hash of data from URL.");
        return;
    }
    if (cacheData == null || !urlHash.equals(computeDataHash(cacheData))) {
        lookupTable = urlData;
        saveJsonToCache(lookupTable);
        System.out.println("Cache updated from URL.");
    }
}

public static Map<String, String> getBranchAndLegalEntity(String country) {
    Map<String, String> result = new HashMap<>();
    JSONArray data = getLookupTable();
    if (data == null) {
        System.err.println("Unable to get data from cache.");
        return result;
    }
    for (int i = 0; i < data.length(); i++) {
        JSONObject obj = data.getJSONObject(i);
        String currCountry = obj.getString("country");
        if (currCountry.equals(country)) {
            String branch = obj.getString("branch");
            String legalEntity = obj.getString("legal_entity");
            result.put(branch, legalEntity);
        }
    }
    return result;
}

}
           