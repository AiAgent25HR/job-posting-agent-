import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Briefcase, Lock } from "lucide-react";
import { toast } from "sonner";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // Dummy login - accepts anything
    setTimeout(() => {
      localStorage.setItem("isAuthenticated", "true");
      toast.success("Login successful!");
      navigate("/");
      setIsLoading(false);
    }, 500);
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="p-3 bg-primary/10 rounded-full">
              <Briefcase className="h-8 w-8 text-primary" />
            </div>
          </div>
          <CardTitle className="text-3xl font-bold">Talent Scout AI</CardTitle>
          <CardDescription className="text-base">
            HR Portal - Sign in to continue
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="h-11"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="h-11"
              />
            </div>

            <Button
              type="submit"
              className="w-full h-11 bg-primary hover:bg-primary/90"
              disabled={isLoading}
            >
              {isLoading ? (
                "Signing in..."
              ) : (
                <>
                  <Lock className="mr-2 h-4 w-4" />
                  Sign In
                </>
              )}
            </Button>
          </form>
          
        </CardContent>
      </Card>
    </div>
  );
};

export default Login;

