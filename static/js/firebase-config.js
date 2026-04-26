// Firebase configuration for pauldejong.com
//
// NOTE: The apiKey below is NOT a secret. Firebase web API keys are public
// identifiers — they identify the project, they don't authenticate. Access
// is controlled by Firebase Security Rules (firestore.rules), Auth
// authorized domains, and HTTP referrer restrictions on the key in GCP.
// See: https://firebase.google.com/docs/projects/api-keys
//
// GitHub secret-scanning will flag this as a "Google API Key" because it
// matches the AIza... pattern. Dismiss as a false positive.
const firebaseConfig = {
  projectId: "pauldejong-com",
  appId: "1:445600985890:web:3ef2fe2bd13a1ba473ab7b",
  storageBucket: "pauldejong-com.firebasestorage.app",
  apiKey: "AIzaSyBOPGwMQWrgQLMM9To1WlmPxh40FcJ7WTs",
  authDomain: "pauldejong-com.firebaseapp.com",
  messagingSenderId: "445600985890",
};
