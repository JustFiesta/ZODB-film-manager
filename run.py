from web import create_app
import sys

if __name__ == "__main__":
    app = create_app()
    
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Run tests
        import unittest
        from tests.test_crud import TestMovieManager
        from tests.test_routes import TestFlaskRoutes
        
        test_suite = unittest.TestSuite()
        test_suite.addTest(unittest.makeSuite(TestMovieManager))
        test_suite.addTest(unittest.makeSuite(TestFlaskRoutes))
        
        runner = unittest.TextTestRunner()
        runner.run(test_suite)
    else:
        # Run web app
        app.run(debug=True, host='0.0.0.0', port=5000)