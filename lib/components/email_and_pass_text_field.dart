import 'package:flutter/material.dart';

class CustomTextField extends StatelessWidget {
  final Color color;
  final Icon icon;
  final String text;
  const CustomTextField(
      {super.key, required this.color, required this.icon, required this.text});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.only(top: 12),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(16),
      ),
      child: TextField(
        style: TextStyle(
          color: Colors.black,
          fontSize: 15,
        ),
        decoration: InputDecoration(
          suffixIcon: icon,
          contentPadding: EdgeInsets.only(left: 20, top: 15, bottom: 15),
          hintText: text,
          hintStyle: TextStyle(color: Colors.grey, fontSize: 15),
          border: InputBorder.none,
        ),
      ),
    );
  }
}
