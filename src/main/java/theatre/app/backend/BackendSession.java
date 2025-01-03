package theatre.app.backend;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import com.datastax.driver.core.Cluster;
import com.datastax.driver.core.Session;

import java.io.IOException;
import java.util.Properties;

@Component
public class BackendSession {

	private static final Logger logger = LoggerFactory.getLogger(BackendSession.class);

	public final Session session;

	public BackendSession() throws BackendException {
		String contactPoint;
		String keyspace;

		// Load properties from the `config.properties` file
		Properties properties = new Properties();
		try {
			properties.load(getClass().getClassLoader().getResourceAsStream("config.properties"));
			contactPoint = properties.getProperty("contact_point");
			keyspace = properties.getProperty("keyspace");
		} catch (IOException ex) {
			throw new BackendException("Failed to load properties file: " + ex.getMessage(), ex);
		}
		System.out.println("DEBUUUUUUUG: contact_point: " + contactPoint);
		System.out.println("DEBUUUUUG: keyspace: " + keyspace);
		// Connect to Cassandra using the loaded properties
		Cluster cluster = Cluster.builder().addContactPoint(contactPoint).build();
		try {
			session = cluster.connect(keyspace);
		} catch (Exception e) {
			throw new BackendException("Could not connect to the cluster. " + e.getMessage() + ".", e);
		}
	}
}
