import { useState } from "react";
import axios from "axios";

/**
 * ExtractMessage component allows users to extract hidden messages from images.
 * It provides a form to submit the image path and password,
 * then displays the extracted message or an error message.
 */
const ExtractMessage = () => {
  const [imagePath, setImagePath] = useState("");
  const [password, setPassword] = useState("");
  const [response, setResponse] = useState("");

  /**
   * Handles the form submission to extract a message from an image.
   * Prevents default form submission, then sends a POST request to the API.
   * Uses optional chaining to safely handle error responses.
   */
  const handleSubmit = async (e: any) => {
    e.preventDefault();
    try {
      const res = await axios.post("http://127.0.0.1:5000/extract", {
        image_path: imagePath,
        password,
      });
      setResponse(res.data.message);
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || error.message;
      setResponse("Error: " + errorMessage);
    }
  };

  return (
    <div className="p-4 max-w-md mx-auto bg-white shadow-md rounded-md">
      <h2 className="text-2xl font-bold mb-4 text-center">
        Extract Message from Image
      </h2>
      <form onSubmit={handleSubmit} className="flex flex-col space-y-4">
        <input
          type="text"
          placeholder="Image Path"
          value={imagePath}
          onChange={(e) => setImagePath(e.target.value)}
          className="border p-2 rounded outline-none focus:ring-2 focus:ring-blue-500"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="border p-2 rounded outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="bg-blue-500 text-white py-2 rounded hover:bg-blue-600 transition-colors"
        >
          Extract Message
        </button>
      </form>
      {response && (
        <p className="mt-4 text-center text-lg">
          {response}
        </p>
      )}
    </div>
  );
};

export default ExtractMessage;