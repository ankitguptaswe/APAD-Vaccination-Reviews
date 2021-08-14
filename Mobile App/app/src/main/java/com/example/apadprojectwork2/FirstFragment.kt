package com.example.apadprojectwork2

import android.content.Intent
import android.graphics.Bitmap
import android.graphics.drawable.BitmapDrawable
import android.os.Bundle
import android.util.Base64
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.android.volley.NetworkResponse
import com.android.volley.Request
import com.android.volley.Response
import com.android.volley.toolbox.HttpHeaderParser
import com.android.volley.toolbox.StringRequest
import com.android.volley.toolbox.Volley
import com.example.apadprojectwork2.databinding.FragmentFirstBinding
import kotlinx.android.synthetic.main.activity_theme.*
import kotlinx.android.synthetic.main.theme_row.*
import java.io.ByteArrayOutputStream
import java.io.IOException
import java.lang.NullPointerException
import java.nio.charset.Charset
import kotlin.coroutines.resume
import kotlin.coroutines.suspendCoroutine

var response_themes : String? = null

/**
 * A simple [Fragment] subclass as the default destination in the navigation.
 */
class FirstFragment : Fragment() {

    private var _binding: FragmentFirstBinding? = null

    // This property is only valid between onCreateView and
    // onDestroyView.
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {

        _binding = FragmentFirstBinding.inflate(inflater, container, false)
        return binding.root

    }

    fun fetchThemes() {
        val queue = Volley.newRequestQueue(this.context)
        val url = "https://apad-vaccine-reviews.uc.r.appspot.com/themes/all"
        val stringRequest = object: StringRequest(
            Method.GET, url,
            Response.Listener { response ->
                val strResp = response.toString()
                var result: List<String> = strResp.split("]").map { it.trim() }
                var themes: List<String> = result[0].drop(1).drop(1).dropLast(1).replace("\"", "").split(",").map { it.trim() }
                var descriptions: List<String> = result[1].drop(1).drop(1).drop(1).dropLast(1).replace("\"", "").split(",").map { it.trim() }
                var pictures: List<String> = result[2].drop(1).drop(1).drop(1).dropLast(1).replace("\"", "").split(",").map { it.trim() }
                val themeFeed = Themes(themes, descriptions, pictures)
                ThemeAdapter(themeFeed)
            },
            Response.ErrorListener {  })
        {
            override fun getHeaders(): MutableMap<String, String> {
                val headers = HashMap<String, String>()
                headers["source"] = "android"
                return headers
            }
        }
        queue.add(stringRequest)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // GET ALL THEMES
        anyFunction(view)

        // POST CONSTRUCTOR
        view.findViewById<Button>(R.id.button_first).setOnClickListener {
            try {
                // TITLE
                // Input from EditText
                val var_title = view.findViewById<EditText>(R.id.th_title)
                val var_title_text = var_title.text.toString()

                // DESCRIPTION
                // Input from EditText
                val var_description = view.findViewById<EditText>(R.id.th_review)
                val var_description_text = var_description.text.toString()

                // THEME
                // Input from EditText
                val var_theme = view.findViewById<Spinner>(R.id.spinner)
                val var_theme_text = var_theme.selectedItem.toString()

                // TAGS
                // Input from EditText
                val var_tags = view.findViewById<EditText>(R.id.th_tags)
                val var_tags_text = var_tags.text.toString()

                // RATING
                // Input from EditText
                val var_rating = view.findViewById<RatingBar>(R.id.star)
                val var_rating_text = var_rating.rating.toInt().toString()

                // IMAGE
                // Get image from imageview
                val var_picture = view.findViewById<ImageView>(R.id.imageView)
                val bitmap = (var_picture.getDrawable() as BitmapDrawable).getBitmap()
                val stream = ByteArrayOutputStream()
                bitmap.compress(Bitmap.CompressFormat.JPEG, 90, stream)
                val image = stream.toByteArray()
                val encodedImage: String = Base64.encodeToString(image, Base64.DEFAULT)

                // LOCATION
                var th_lat = location_user_lat.toString()
                var th_lng = location_user_lng.toString()
                var user_id = "android_user"

                if (location_user_lat.isNullOrEmpty() || location_user_lng.isNullOrEmpty()) {
                    throw NullPointerException()
                }
                if (var_title_text.isNullOrEmpty() || var_rating_text.isNullOrEmpty() || var_theme_text.isNullOrEmpty()) {
                    throw IOException("Please fill all details")
                }
                //anyFunction(view)
                otherFunction(view, var_theme_text, var_title_text, var_description_text, var_rating_text, var_tags_text, encodedImage, th_lat, th_lng, user_id)
                onReviewCreateClick()
                Toast.makeText(getActivity()?.applicationContext, "Review succesfully posted", Toast.LENGTH_SHORT).show()
            } catch (e : NullPointerException) {
                Toast.makeText(
                    getActivity()?.applicationContext,
                    "Please provide location permission to the application",
                    Toast.LENGTH_SHORT
                ).show()
            }
            catch (e : Exception){
                Toast.makeText(getActivity()?.applicationContext, "Please fill all details", Toast.LENGTH_SHORT).show()
            }
        }
    }

    fun onReviewCreateClick() {
        val intent = Intent (getActivity(), ProfileActivity::class.java)
        getActivity()?.startActivity(intent)
    }

    fun anyFunction(view: View) {

        // TUTO
        // Instantiate the RequestQueue.
        val queue = Volley.newRequestQueue(this.context)
        val url: String = "https://apad-vaccine-reviews.uc.r.appspot.com/themes/all"

        val stringRequest = object: StringRequest(
            Method.GET, url,
            Response.Listener<String> { response ->
                var strResp = response.toString()
                Log.d("Response get from themes route", strResp)
                setThemes(strResp)
            },
            Response.ErrorListener {  })
        {
            override fun getHeaders(): MutableMap<String, String> {
                val headers = HashMap<String, String>()
                headers["source"] = "android"
                return headers
            }
        }

        queue.add(stringRequest)
    }

    private fun setThemes(strResp: String) {

        var result: List<String> = strResp.split("]").map { it.trim() }
        var themes: List<String> = result[0].drop(1).drop(1).dropLast(1).replace("\"", "").split(",").map { it.trim() }

        val spinner: Spinner = view!!.findViewById(R.id.spinner)

        this.context?.let {
            ArrayAdapter(
                it,
                android.R.layout.simple_spinner_item,
                themes
            ).also { adapter ->
                // Specify the layout to use when the list of choices appears
                adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
                // Apply the adapter to the spinner
                spinner.adapter = adapter
            }
        }

    }


    fun otherFunction(view: View, th_preferences: String, th_title: String, th_review: String, star: String, th_tags: String, th_photo: String, th_lat: String, th_lng: String, user_id: String) {
        // TUTO
        // Instantiate the RequestQueue.
        val queue = Volley.newRequestQueue(this.context)
        val url: String = "https://apad-vaccine-reviews.uc.r.appspot.com/reviews/create/android"

        val stringRequest = object: StringRequest(
            Method.POST, url,
            Response.Listener<String> { response ->
                var strResp = response.toString()
                Log.d("Post review", strResp)
            },
            Response.ErrorListener {  })
        {
            override fun getParams(): Map<String, String> {
                val params: MutableMap<String, String> = HashMap()
                //Change with your post params
                params["th_preferences"] = th_preferences
                params["th_title"] = th_title
                params["th_review"] = th_review
                params["star"] = star
                params["th_tags"] = th_tags
                params["th_photo"] = th_photo
                params["th_lat"] = th_lat
                params["th_lng"] = th_lng
                params["user_id"] = user_id

                return params

                //return requestBody.toByteArray(Charset.defaultCharset())
            }

            override fun getHeaders(): MutableMap<String, String> {
                val headers = HashMap<String, String>()
                headers["source"] = "android"
                return headers
            }
        }

        queue.add(stringRequest)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
