import 'package:flutter/material.dart';
import 'package:workoutwise/src/weight_selection.dart';

class HeightSelection extends StatefulWidget {
  @override
  _HeightSelectionState createState() => _HeightSelectionState();
}

class _HeightSelectionState extends State<HeightSelection> {
  // Initial height value
  int selectedHeight = 180;

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;
    return Scaffold(
      backgroundColor: Colors.black,
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
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
                SizedBox(width: screenWidth * 0.001), // 2% of screen width
                for (int i = 2; i < 4; i++)
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
          SizedBox(height: screenHeight * 0.02),
          // Title
          const Text(
            "How tall are you?",
            style: TextStyle(
              color: Color(0xff7C4DFF),
              fontSize: 30,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 10),
          // Unit label
          const Text(
            "Centimeter",
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 30),
          // Height Selection Scroller
          Expanded(
            child: Stack(
              alignment: Alignment.center,
              children: [
                ListWheelScrollView.useDelegate(
                  itemExtent: 60,
                  physics: const FixedExtentScrollPhysics(),
                  perspective: 0.003,
                  onSelectedItemChanged: (index) {
                    setState(() {
                      selectedHeight = 165 + index;
                    });
                  },
                  childDelegate: ListWheelChildBuilderDelegate(
                    builder: (context, index) {
                      final heightValue = 165 + index;
                      return Text(
                        heightValue.toString(),
                        style: TextStyle(
                          fontSize: heightValue == selectedHeight ? 35 : 24,
                          color: heightValue == selectedHeight
                              ? Color(0xff7C4DFF)
                              : Colors.grey,
                          fontWeight: heightValue == selectedHeight
                              ? FontWeight.bold
                              : FontWeight.normal,
                        ),
                      );
                    },
                    childCount: 50, // Ranges from 165 to 215
                  ),
                ),
                Positioned(
                  right: 100,
                  child: Text(
                    "Cm",
                    style: TextStyle(color: Colors.grey, fontSize: 16),
                  ),
                ),
              ],
            ),
          ),
          // Continue Button
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: ElevatedButton(
              onPressed: () {
                // Action on continue
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => WeightSelectionScreen(),
                  ),
                );
                print("Selected Height: $selectedHeight cm");
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
