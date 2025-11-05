package com.org.pragatidhara.activity

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.org.pragatidhara.databinding.ActivityVehicleDetailsBinding
import com.org.pragatidhara.R

class VehicleDetailsActivity : AppCompatActivity() {

    private lateinit var binding: ActivityVehicleDetailsBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityVehicleDetailsBinding.inflate(layoutInflater)
        setContentView(binding.root)

        val fullName = intent.getStringExtra("fullName")
        val mobileNumber = intent.getStringExtra("mobileNumber")

        binding.btnFetchDetails.setOnClickListener {
            // Read and normalize inputs
            var regNumber = binding.etVehicleRegNumber.text.toString().trim().uppercase()
            val chasisNumber = binding.etChasisNumber.text.toString().trim().uppercase()

            // validations
            if (regNumber.isEmpty()) {
                Toast.makeText(this, "Please enter vehicle registration number", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            if (chasisNumber.length != 5) {
                Toast.makeText(this, "Chassis number must be exactly 5 characters", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            // put normalized reg number back to EditText so user sees CAPS
            binding.etVehicleRegNumber.setText(regNumber)
            binding.etChasisNumber.setText(chasisNumber)

            // Mock API call to fetch vehicle details
            binding.llVehicleDetails.visibility = View.VISIBLE

            // Populate visible details (mock data)
            binding.tvVehicleMakeModel.text = "Vehicle Make and Model: Honda City"
            binding.tvFuelType.text = "Fuel Type: Petrol"
            binding.tvEngineCapacity.text = "Engine Capacity: 1498cc"
            binding.tvRegistrationDate.text = "Date of Registration: 01-01-2022"
            binding.tvPucExpiry.text = "Last PUC Expiry Date: 31-12-2023"
            binding.tvEmissionLevels.text = "Emission Levels: CO: 0.5, HC: 50"

            // keep values available on tag for submit dialog
            binding.btnFetchDetails.tag = mapOf(
                "owner" to (fullName ?: ""),
                "mobile" to (mobileNumber ?: ""),
                "reg" to regNumber,
                "chasis" to chasisNumber,
                "make" to "Honda City",
                "fuel" to "Petrol",
                "engine" to "1498cc",
                "regdate" to "01-01-2022",
                "puc" to "31-12-2023"
            )
            var data = binding.btnFetchDetails.tag as Map<String, String> ;
            // show the Dialog with details for confirmation
            // Inflate dialog layout and fill values
            val dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_vehicle_details, null)
            (dialogView.findViewById<TextView>(R.id.value_owner)).text = data["owner"] as? String ?: ""
            (dialogView.findViewById<TextView>(R.id.value_mobile)).text = data["mobile"] as? String ?: ""
            (dialogView.findViewById<TextView>(R.id.value_reg)).text = data["reg"] as? String ?: ""
            (dialogView.findViewById<TextView>(R.id.value_chasis)).text = data["chasis"] as? String ?: ""
            (dialogView.findViewById<TextView>(R.id.value_make)).text = data["make"] as? String ?: ""
            (dialogView.findViewById<TextView>(R.id.value_fuel)).text = data["fuel"] as? String ?: ""
            (dialogView.findViewById<TextView>(R.id.value_engine)).text = data["engine"] as? String ?: ""
            (dialogView.findViewById<TextView>(R.id.value_regdate)).text = data["regdate"] as? String ?: ""
            (dialogView.findViewById<TextView>(R.id.value_puc)).text = data["puc"] as? String ?: ""

            val dialog = AlertDialog.Builder(this)
                .setTitle("Confirm Vehicle Details")
                .setView(dialogView)
                .setPositiveButton("Confirm") { _, _ ->
                    Toast.makeText(this, "Details submitted for ${data["owner"]}", Toast.LENGTH_SHORT).show()
                    val intent = Intent(this, MainActivity::class.java)
                    startActivity(intent)
                    finishAffinity()
                }
                .setNegativeButton("Edit") { d, _ -> d.dismiss() }
                .create()

            dialog.show()

        }


    }
}