import { useState } from "react";
import axios from "axios";

const HideMessage = () => {
  const [inputImage, setInputImage] = useState("");
  const [outputImage, setOutputImage] = useState("");
  const [message, setMessage] = useState("");
  const [password, setPassword] = useState("");
  const [response, setResponse] = useState("");

  const handleSubmit = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:5000/hide", {
        input_image: inputImage,
        output_image: outputImage,
        message,
        password,
      });
      setResponse(res.data.message);
    } catch (error: any) {
      setResponse("Error: " + (error.response?.data?.error || error.message));
    }
  };

  return (
    <div>
      <h2>Hide Message in Image</h2>
      <input
        type="text"
        placeholder="Input Image Path"
        value={inputImage}
        onChange={(e) => setInputImage(e.target.value)}
      />
      <input
        type="text"
        placeholder="Output Image Path"
        value={outputImage}
        onChange={(e) => setOutputImage(e.target.value)}
      />
      <input
        type="text"
        placeholder="Message"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={handleSubmit}>Hide Message</button>
      {response && <p>{response}</p>}
    </div>
  );
};

export default HideMessage;