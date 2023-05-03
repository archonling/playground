import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.HashMap;
import java.util.Map;

import org.apache.commons.io.FileUtils;
import org.json.JSONArray;
import org.json.JSONObject;

public class LookupTable2 {
    private static final String CACHE_FILE_PREFIX = "lookup_table_";
    private static final String CACHE_FILE_SUFFIX = ".json";
    private static final String JSON_URL = "https://example.com/lookup_table.json";
    private static final long DEFAULT_CACHE_EXPIRY = 15 * 60 * 1000; // 15 minutes

    private HashMap<String, CacheData> cache;
    private Path cacheFile;
    private long cacheExpiry;
    private Instant cacheExpiryTime;

    public class CacheData {
        private String country;
        private String lvid;
        private String giwBranch;
        
        public CacheData(String country, String lvid, String giwBranch) {
            this.country = country;
            this.lvid = lvid;
            this.giwBranch = giwBranch;
        }
        
        public String getCountry() {
            return country;
        }
        
        public String getLvid() {
            return lvid;
        }
        
        public String getGiwBranch() {
            return giwBranch;
        }
    }

    public LookupTable2() throws IOException {
        this(DEFAULT_CACHE_EXPIRY);
    }

    public LookupTable2(long cacheExpiry) throws IOException {
        this.cacheExpiry = cacheExpiry;
        this.cache = new HashMap<String, CacheData>();
        this.cacheFile = createCacheFile();
        this.cacheExpiryTime = Instant.now().plus(cacheExpiry, ChronoUnit.MILLIS);
        refreshCache();
    }

    private Path createCacheFile() throws IOException {
        String cacheFileName = CACHE_FILE_PREFIX + System.currentTimeMillis() + CACHE_FILE_SUFFIX;
        File cacheDirectory = new File(System.getProperty("java.io.tmpdir"));
        Path cacheFilePath = Paths.get(cacheDirectory.getAbsolutePath(), cacheFileName);
        Files.createFile(cacheFilePath);
        return cacheFilePath;
    }

    private void downloadJsonFile() throws IOException {
        FileUtils.copyURLToFile(new URL(JSON_URL), cacheFile.toFile(), 10000, 10000);
    }

    private void refreshCache() throws IOException {
        if (Instant.now().isAfter(cacheExpiryTime)) {
            downloadJsonFile();
            cache.clear();

            JSONObject jsonObject = new JSONObject(FileUtils.readFileToString(cacheFile.toFile(), "UTF-8"));
            JSONArray jsonArray = jsonObject.getJSONArray("lookup");

            for (int i = 0; i < jsonArray.length(); i++) {
                JSONObject row = jsonArray.getJSONObject(i);                
                String countryCode = row.getString("country_code");
                String giwBranch = row.getString("giw_branch");
                String lvid = row.getString("lvid");
                cache.put(giwBranch, new CacheData(countryCode, lvid, giwBranch));
            }

            cacheExpiryTime = Instant.now().plus(cacheExpiry, ChronoUnit.MILLIS);
        }
    }

    public CacheData getCountryAndLegalEntity(String giwBranch) throws IOException {        
        refreshCache();
        return cache.get(giwBranch);
    }

    public void close() throws IOException {
        Files.deleteIfExists(cacheFile);
    }
}
