import java.io.FileReader;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

public class JsonParser {
    public static void main(String[] args) throws Exception {
        // read the JSON file into a String
        String json = new String(Files.readAllBytes(Paths.get("file.json")));

        // create a Gson instance
        Gson gson = new Gson();

        // parse the JSON array into a Java array
        TypeToken<JsonData[]> token = new TypeToken<JsonData[]>() {};
        JsonData[] data = gson.fromJson(json, token.getType());

        // print out the data
        for (JsonData d : data) {
            System.out.println("Country Code: " + d.countryCode);
            System.out.println("LVID: " + d.lvid);
            System.out.println("GIW Branch: " + d.giwBranch);
        }
    }
}

class JsonData {
    String countryCode;
    String lvid;
    String giwBranch;
}
