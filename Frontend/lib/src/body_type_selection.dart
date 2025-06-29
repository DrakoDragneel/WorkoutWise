import 'package:flutter/material.dart';
import 'package:workoutwise/src/height_selection.dart';

class BodyTypeSelection extends StatelessWidget {
  const BodyTypeSelection({super.key});

  @override
  Widget build(BuildContext context) {
    // Get screen height and width
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;

    return Scaffold(
      backgroundColor: Color(0xff111213),
      body: Column(
        children: [
          SizedBox(
              height: screenHeight * 0.05), // Top padding (5% of screen height)
          // Progress Bar
          Row(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              SizedBox(
                width: screenWidth * 0.05,
              ),
              CircleAvatar(
                backgroundColor: Colors.white,
                child: IconButton(
                    onPressed: () {
                      Navigator.pop(context);
                    },
                    icon: Icon(Icons.arrow_back)),
              ),
              SizedBox(
                width: screenWidth * 0.09,
              ),
              Container(
                height: screenHeight * 0.01, // 1% of screen height
                width: screenWidth * 0.1, // 10% of screen width
                decoration: BoxDecoration(
                  color: Color(0xff7C4DFF),
                  borderRadius: BorderRadius.circular(screenHeight * 0.02),
                ),
              ),
              SizedBox(width: screenWidth * 0.02), // 2% of screen width
              Container(
                height: screenHeight * 0.01, // 1% of screen height
                width: screenWidth * 0.1, // 10% of screen width
                decoration: BoxDecoration(
                  color: Color(0xff7C4DFF),
                  borderRadius: BorderRadius.circular(screenHeight * 0.02),
                ),
              ),
              SizedBox(width: screenWidth * 0.001), // 2% of screen width
              for (int i = 1; i < 4; i++)
                Container(
                  height: screenHeight * 0.01,
                  width: screenWidth * 0.1,
                  margin: EdgeInsets.only(left: screenWidth * 0.02),
                  decoration: BoxDecoration(
                    color: Colors.grey[800],
                    borderRadius: BorderRadius.circular(screenHeight * 0.02),
                  ),
                ),
            ],
          ),
          SizedBox(height: screenHeight * 0.18),
          // Title
          Text(
            "What is your Fitness Goal?",
            style: TextStyle(
              color: Color(0xff7C4DFF),
              fontSize: 30,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: screenHeight * 0.09),
          // Gender Buttons
          Padding(
            padding: EdgeInsets.symmetric(horizontal: screenWidth * 0.05),
            child: Column(
              children: [
                ElevatedButton(
                  onPressed: () {},
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.black,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(screenHeight * 0.02),
                      side: BorderSide(color: Colors.white),
                    ),
                    minimumSize: Size(double.infinity, screenHeight * 0.07),
                  ),
                  child: Text(
                    "Build Muscle",
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: screenWidth * 0.045, // Scaled font size
                    ),
                  ),
                ),

                SizedBox(
                    height: screenHeight *
                        0.03), // Space between buttons (3% of screen height)
                ElevatedButton(
                  onPressed: () {},
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.black,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(screenHeight * 0.02),
                      side: BorderSide(color: Colors.white),
                    ),
                    minimumSize: Size(double.infinity, screenHeight * 0.07),
                  ),
                  child: Text(
                    "Get Fit",
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: screenWidth * 0.045,
                    ),
                  ),
                ),
                SizedBox(
                    height: screenHeight *
                        0.03), // Space between buttons (3% of screen height)
                ElevatedButton(
                  onPressed: () {},
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.black,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(screenHeight * 0.02),
                      side: BorderSide(color: Colors.white),
                    ),
                    minimumSize: Size(double.infinity, screenHeight * 0.07),
                  ),
                  child: Text(
                    "Lose Weight",
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: screenWidth * 0.045,
                    ),
                  ),
                ),
              ],
            ),
          ),

          SizedBox(
            height: screenHeight * 0.10,
          ),
          // Continue Button
          Padding(
            padding: EdgeInsets.symmetric(horizontal: screenWidth * 0.05),
            child: ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => HeightSelection(),
                  ),
                );
              },
              style: ElevatedButton.styleFrom(
                primary: Color(0xff7C4DFF),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(screenHeight * 0.025),
                ),
                minimumSize: Size(double.infinity, screenHeight * 0.07),
              ),
              child: Text(
                "Continue",
                style: TextStyle(
                  color: Colors.white,
                  fontSize: screenWidth * 0.045,
                ),
              ),
            ),
          ),
          SizedBox(
              height:
                  screenHeight * 0.05), // Bottom padding (5% of screen height)
        ],
      ),
    );
  }
}
