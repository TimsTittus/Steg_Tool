import React, { useState } from 'react';
import { Upload, FileText } from 'lucide-react';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Card, CardHeader, CardContent, CardTitle } from './components/ui/card';
import { Alert, AlertDescription } from './components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';

const SteganographyTool = () => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [password, setPassword] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);
  const [extractedMessage, setExtractedMessage] = useState('');

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleHideMessage = async () => {
    if (!selectedFile || !message || !password) {
      setResult({
        success: false,
        message: 'Please provide an image, message, and password',
      });
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('message', message);
    formData.append('password', password);

    try {
      const response = await fetch('http://localhost:8000/api/steganography/hide', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'stego_image.png';
        a.click();
        window.URL.revokeObjectURL(url);

        setResult({
          success: true,
          message: 'Message hidden successfully! Image downloaded.',
        });
      } else {
        const error = await response.json();
        setResult({
          success: false,
          message: error.message || 'Failed to hide message',
        });
      }
    } catch (error) {
      setResult({
        success: false,
        message: 'An error occurred while processing your request',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExtractMessage = async () => {
    if (!selectedFile || !password) {
      setResult({
        success: false,
        message: 'Please provide an image and password',
      });
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('password', password);

    try {
      const response = await fetch('/api/steganography/extract', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (response.ok) {
        setExtractedMessage(data.message);
        setResult({
          success: true,
          message: 'Message extracted successfully!',
        });
      } else {
        setResult({
          success: false,
          message: data.message || 'Failed to extract message',
        });
      }
    } catch (error) {
      setResult({
        success: false,
        message: 'An error occurred while processing your request',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Image Steganography Tool</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="hide">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="hide">Hide Message</TabsTrigger>
            <TabsTrigger value="extract">Extract Message</TabsTrigger>
          </TabsList>

          <TabsContent value="hide">
            <div className="space-y-4">
              <div className="grid w-full items-center gap-1.5">
                <Input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="cursor-pointer"
                />
              </div>

              <div className="grid w-full items-center gap-1.5">
                <Input
                  type="text"
                  placeholder="Enter your message"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                />
              </div>

              <div className="grid w-full items-center gap-1.5">
                <Input
                  type="password"
                  placeholder="Enter password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              <Button
                className="w-full"
                onClick={handleHideMessage}
                disabled={loading}
              >
                {loading ? (
                  'Processing...'
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" />
                    Hide Message
                  </>
                )}
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="extract">
            <div className="space-y-4">
              <div className="grid w-full items-center gap-1.5">
                <Input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="cursor-pointer"
                />
              </div>

              <div className="grid w-full items-center gap-1.5">
                <Input
                  type="password"
                  placeholder="Enter password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              <Button
                className="w-full"
                onClick={handleExtractMessage}
                disabled={loading}
              >
                {loading ? (
                  'Processing...'
                ) : (
                  <>
                    <FileText className="mr-2 h-4 w-4" />
                    Extract Message
                  </>
                )}
              </Button>

              {extractedMessage && (
                <Card className="mt-4">
                  <CardContent className="pt-4">
                    <p className="font-medium">Extracted Message:</p>
                    <p className="mt-2">{extractedMessage}</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>
        </Tabs>

        {result && (
          <Alert className={`mt-4 ${result.success ? 'bg-green-50' : 'bg-red-50'}`}>
            <AlertDescription>{result.message}</AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default SteganographyTool;