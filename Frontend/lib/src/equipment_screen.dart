import 'package:flutter/material.dart';

class EquipmentSelectionScreen extends StatefulWidget {
  @override
  _EquipmentSelectionScreenState createState() =>
      _EquipmentSelectionScreenState();
}

class _EquipmentSelectionScreenState extends State<EquipmentSelectionScreen> {
  // List of equipment options
  final List<String> equipmentOptions = [
    "Dumbbells",
    "Resistance Bands",
    "Yoga Mat",
    "Kettlebell",
    "Stationary Bike"
  ];

  // Map to track the selection status of each equipment
  Map<String, bool> selectedOptions = {};

  @override
  void initState() {
    super.initState();
    // Initialize all options as unselected
    for (var option in equipmentOptions) {
      selectedOptions[option] = false;
    }
  }

  @override
  Widget build(BuildContext context) {
    // Get screen dimensions
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;

    return Scaffold(
      backgroundColor: Colors.black,
      body: Padding(
        padding: EdgeInsets.symmetric(horizontal: screenWidth * 0.04),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            SizedBox(
              height: screenHeight * 0.05,
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.start,
              children: [
                CircleAvatar(
                  backgroundColor: Colors.white,
                  child: IconButton(
                    onPressed: () {
                      Navigator.pop(context);
                    },
                    icon: Icon(Icons.arrow_back),
                  ),
                ),
                SizedBox(
                  width: screenWidth * 0.09,
                ),
              ],
            ),
            // Title
            SizedBox(height: screenHeight * 0.02),
            Text(
              "What Type of Equipment You have in your home?",
              textAlign: TextAlign.center,
              style: TextStyle(
                color: const Color(0xff7C4DFF),
                fontSize: screenWidth * 0.08, // Responsive font size
                fontWeight: FontWeight.w700,
              ),
            ),
            SizedBox(height: screenHeight * 0.04),
            // Equipment Options List
            Expanded(
              child: ListView.builder(
                itemCount: equipmentOptions.length,
                itemBuilder: (context, index) {
                  String option = equipmentOptions[index];
                  return Container(
                    margin: EdgeInsets.symmetric(vertical: screenHeight * 0.01),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(30),
                    ),
                    child: CheckboxListTile(
                      title: Text(
                        option,
                        style: TextStyle(
                          color: Colors.black,
                          fontSize: screenWidth * 0.04, // Responsive font size
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      value: selectedOptions[option],
                      activeColor: Colors.purple,
                      onChanged: (bool? value) {
                        setState(() {
                          selectedOptions[option] = value!;
                        });
                      },
                      controlAffinity: ListTileControlAffinity.trailing,
                    ),
                  );
                },
              ),
            ),
            SizedBox(height: screenHeight * 0.03),
            // Skip Button
            Padding(
              padding: EdgeInsets.symmetric(horizontal: screenWidth * 0.03),
              child: ElevatedButton(
                onPressed: () {
                  // Action on skip
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.grey.shade800,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(24),
                  ),
                  padding: EdgeInsets.symmetric(vertical: screenHeight * 0.02),
                ),
                child: Center(
                  child: Text(
                    "Skip",
                    style: TextStyle(
                      fontSize: screenWidth * 0.045, // Responsive font size
                      color: Colors.white,
                    ),
                  ),
                ),
              ),
            ),
            SizedBox(height: screenHeight * 0.015),
            // Continue Button
            Padding(
              padding: EdgeInsets.symmetric(horizontal: screenWidth * 0.03),
              child: ElevatedButton(
                onPressed: () {
                  // Action on continue
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xff7C4DFF),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(24),
                  ),
                  padding: EdgeInsets.symmetric(vertical: screenHeight * 0.02),
                ),
                child: Center(
                  child: Text(
                    "Continue",
                    style: TextStyle(
                      fontSize: screenWidth * 0.045, // Responsive font size
                      color: Colors.white,
                    ),
                  ),
                ),
              ),
            ),
            SizedBox(height: screenHeight * 0.02),
          ],
        ),
      ),
    );
  }
}
