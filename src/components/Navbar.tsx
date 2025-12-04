import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Briefcase, Home, Plus, List, LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("isAuthenticated");
    navigate("/login");
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="bg-primary border-b border-primary/20 shadow-sm">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link to="/" className="flex items-center gap-2 text-primary-foreground hover:text-primary-foreground/80">
              <Briefcase className="h-6 w-6" />
              <span className="text-xl font-bold">Talent Scout AI</span>
            </Link>
            
            <div className="flex items-center gap-2">
              <Button
                variant={isActive("/") ? "secondary" : "ghost"}
                size="sm"
                onClick={() => navigate("/")}
                className="text-primary-foreground hover:text-primary-foreground"
              >
                <Home className="mr-2 h-4 w-4" />
                Home
              </Button>
              
              <Button
                variant={isActive("/create-posting") ? "secondary" : "ghost"}
                size="sm"
                onClick={() => navigate("/create-posting")}
                className="text-primary-foreground hover:text-primary-foreground"
              >
                <Plus className="mr-2 h-4 w-4" />
                Create Posting
              </Button>
              
              <Button
                variant={isActive("/postings") ? "secondary" : "ghost"}
                size="sm"
                onClick={() => navigate("/postings")}
                className="text-primary-foreground hover:text-primary-foreground"
              >
                <List className="mr-2 h-4 w-4" />
                View Postings
              </Button>
            </div>
          </div>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            className="text-primary-foreground hover:text-primary-foreground"
          >
            <LogOut className="mr-2 h-4 w-4" />
            Logout
          </Button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

