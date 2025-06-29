import 'package:flutter/material.dart';
import 'package:numberpicker/numberpicker.dart';
import 'package:workoutwise/src/home_screen.dart';

class WeightSelectionScreen extends StatefulWidget {
  const WeightSelectionScreen({Key? key}) : super(key: key);

  @override
  State<WeightSelectionScreen> createState() => _WeightSelectionScreenState();
}

class _WeightSelectionScreenState extends State<WeightSelectionScreen> {
  int _currentValue = 0;

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;
    return Scaffold(
      backgroundColor: Color(0xff111213),
      body: Column(
        children: [
          SizedBox(height: screenHeight * 0.05),
          // Progress Bar
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.start,
              children: [
                CircleAvatar(
                  backgroundColor: Colors.white,
                  child: IconButton(
                      onPressed: () {
                        Navigator.pop(context);
                      },
                      icon: Icon(
                        Icons.arrow_back,
                      )),
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
                SizedBox(
                  width: screenWidth * 0.02,
                ),
                Container(
                  height: screenHeight * 0.01, // 1% of screen height
                  width: screenWidth * 0.1, // 10% of screen width
                  decoration: BoxDecoration(
                    color: Color(0xff7C4DFF),
                    borderRadius: BorderRadius.circular(screenHeight * 0.02),
                  ),
                ),
                SizedBox(
                  width: screenWidth * 0.02,
                ),
                Container(
                  height: screenHeight * 0.01, // 1% of screen height
                  width: screenWidth * 0.1, // 10% of screen width
                  decoration: BoxDecoration(
                    color: Color(0xff7C4DFF),
                    borderRadius: BorderRadius.circular(screenHeight * 0.02),
                  ),
                ),
                SizedBox(width: screenWidth * 0.001), // 2% of screen width
                for (int i = 3; i < 4; i++)
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
          ),
          SizedBox(height: screenHeight * 0.25),

          Text(
            "What is your Weight?",
            style: TextStyle(
              color: Color(0xff7C4DFF),
              fontSize: 30,
              fontWeight: FontWeight.bold,
            ),
          ),
          
          SizedBox(
            height: screenHeight * 0.23,
          ),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: ElevatedButton(
              onPressed: () {
                // Action on continue
                Navigator.push(context , MaterialPageRoute(builder: (_)=>HomeScreen(),),);
                print("Selected Weight: ${_currentValue} kg");
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Color(0xff7C4DFF),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(24),
                ),
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: const Center(
                child: Text(
                  "Continue",
                  style: TextStyle(fontSize: 16, color: Colors.white),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}


